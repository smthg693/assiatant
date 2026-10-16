"""Direct Judge0 CE execution provider.

Provides a clean abstraction for running code in sandboxed environments using
the direct Judge0 CE API (ce.judge0.com or self-hosted).

Handles:
- Dynamic Python language discovery against the configured endpoint
- Submission creation (POST /submissions?base64_encoded=false&wait=false)
- Result polling with bounded retries, configurable poll interval, and max poll time
- Direct Judge0 auth (X-Auth-Token only when API key is provided)
- HTTP errors, rate limits (429), timeouts, and service unavailability
- Normalized outcomes: passed, wrong_output, runtime_error, timeout
- Explicit separation of infrastructure errors from learner code errors
"""

from __future__ import annotations

import asyncio
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import httpx

from config import get_settings

logger = logging.getLogger(__name__)


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    RUNTIME_ERROR = "runtime_error"
    TIMEOUT = "timeout"
    COMPILATION_ERROR = "compilation_error"
    INTERNAL_ERROR = "internal_error"


@dataclass
class ExecutionResult:
    """Result from executing code in a sandboxed environment."""
    status: ExecutionStatus
    stdout: str = ""
    stderr: str = ""
    exit_code: Optional[int] = None
    time_seconds: Optional[float] = None
    memory_kb: Optional[int] = None
    error_message: str = ""


class ExecutionProvider(ABC):
    """Abstract base class for code execution providers."""

    @abstractmethod
    async def execute(
        self,
        source_code: str,
        stdin: str = "",
        timeout_seconds: Optional[float] = None,
    ) -> ExecutionResult:
        """Execute source code and return the result."""
        ...

    @abstractmethod
    async def is_healthy(self) -> bool:
        """Check if the execution provider is available."""
        ...


# Judge0 status ID mapping
# See: https://ce.judge0.com/statuses
JUDGE0_STATUS = {
    1: "In Queue",
    2: "Processing",
    3: "Accepted",          # Successful execution
    4: "Wrong Answer",      # Output compared server-side
    5: "Time Limit Exceeded",
    6: "Compilation Error",
    7: "Runtime Error (SIGSEGV)",
    8: "Runtime Error (SIGXFSZ)",
    9: "Runtime Error (SIGFPE)",
    10: "Runtime Error (SIGABRT)",
    11: "Runtime Error (NZEC)",
    12: "Runtime Error (Other)",
    13: "Internal Error",
    14: "Exec Format Error",
}


def _map_judge0_status(status_id: int) -> ExecutionStatus:
    """Map Judge0 status ID to our ExecutionStatus enum."""
    if status_id == 3:
        return ExecutionStatus.SUCCESS
    elif status_id == 5:
        return ExecutionStatus.TIMEOUT
    elif status_id == 6:
        return ExecutionStatus.COMPILATION_ERROR
    elif status_id == 13:
        return ExecutionStatus.INTERNAL_ERROR
    elif 7 <= status_id <= 12 or status_id == 14:
        return ExecutionStatus.RUNTIME_ERROR
    else:
        return ExecutionStatus.INTERNAL_ERROR


async def discover_python_language_id(
    base_url: str,
    headers: dict[str, str],
    timeout: float = 10.0,
) -> Optional[int]:
    """Discover the Python 3 language ID from the Judge0 endpoint.
    
    Queries GET /languages and finds modern Python 3.x versions.
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{base_url}/languages", headers=headers)
            if resp.status_code != 200:
                logger.warning("Judge0 language discovery returned HTTP %s", resp.status_code)
                return None
            
            languages = resp.json()
            if not isinstance(languages, list):
                return None
            
            py3_candidates = []
            for lang in languages:
                name = lang.get("name", "")
                lang_id = lang.get("id")
                if not lang_id or not isinstance(name, str):
                    continue
                # Ignore Python 2.x
                if "python (2." in name.lower() or "python 2" in name.lower():
                    continue
                if "python" in name.lower():
                    py3_candidates.append((lang_id, name))
            
            if not py3_candidates:
                return None
            
            # Prioritize: 3.11, 3.12, 3.13, 3.10, 3.8, or any Python 3
            def _version_priority(item):
                lang_id, name = item
                m = re.search(r'python\s*\(([0-9]+(?:\.[0-9]+)*)', name, re.IGNORECASE)
                if m:
                    ver_str = m.group(1)
                    parts = [int(p) for p in ver_str.split(".") if p.isdigit()]
                    if len(parts) >= 2 and parts[0] == 3:
                        if parts[1] == 11:
                            return 100
                        if parts[1] == 12:
                            return 90
                        if parts[1] == 10:
                            return 80
                        if parts[1] == 8:
                            return 70
                        return parts[1]
                if "python 3" in name.lower():
                    return 50
                return 10
            
            py3_candidates.sort(key=_version_priority, reverse=True)
            chosen_id, chosen_name = py3_candidates[0]
            logger.info("Discovered Python language ID on Judge0: %s ('%s')", chosen_id, chosen_name)
            return int(chosen_id)
            
    except Exception as e:
        logger.warning("Judge0 language discovery failed: %s", str(e))
        return None


class Judge0ExecutionProvider(ExecutionProvider):
    """Direct Judge0 CE execution provider.
    
    Submits code to Judge0, polls with bounded retries and configurable timeouts.
    Does not require RapidAPI.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_url = self.settings.judge0_base_url.rstrip("/")
        self._discovered_language_id: Optional[int] = None

    def _headers(self) -> dict[str, str]:
        """Build request headers with optional direct Judge0 auth."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.settings.judge0_api_key:
            headers["X-Auth-Token"] = self.settings.judge0_api_key
        return headers

    async def get_language_id(self) -> int:
        """Resolve the Python language ID:
        1. Use configured JUDGE0_LANGUAGE_ID if set.
        2. Use cached discovered language ID if available.
        3. Discover from the endpoint via /languages.
        4. Fallback to default 71 (Python 3.8).
        """
        if self.settings.judge0_language_id is not None:
            return self.settings.judge0_language_id
        
        if self._discovered_language_id is not None:
            return self._discovered_language_id
        
        discovered = await discover_python_language_id(
            base_url=self.base_url,
            headers=self._headers(),
            timeout=self.settings.judge0_request_timeout,
        )
        if discovered is not None:
            self._discovered_language_id = discovered
            return discovered
        
        logger.warning("Defaulting to language ID 71 for Python 3")
        return 71

    async def execute(
        self,
        source_code: str,
        stdin: str = "",
        timeout_seconds: Optional[float] = None,
    ) -> ExecutionResult:
        """Submit code to direct Judge0 CE and poll for result."""
        language_id = await self.get_language_id()
        exec_timeout = timeout_seconds or self.settings.judge0_execution_timeout

        payload = {
            "source_code": source_code,
            "language_id": language_id,
            "stdin": stdin,
            "cpu_time_limit": str(exec_timeout),
            "wall_time_limit": str(exec_timeout + 5),
            "memory_limit": 128000,  # 128 MB
            "enable_network": False,
        }

        try:
            async with httpx.AsyncClient(timeout=self.settings.judge0_request_timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/submissions?base64_encoded=false&wait=false",
                    headers=self._headers(),
                    json=payload,
                )

                if resp.status_code == 429:
                    return ExecutionResult(
                        status=ExecutionStatus.INTERNAL_ERROR,
                        error_message="Judge0 rate limit exceeded. Please try again shortly.",
                    )

                if resp.status_code in (500, 502, 503, 504):
                    logger.error("Judge0 unavailable: HTTP %s", resp.status_code)
                    return ExecutionResult(
                        status=ExecutionStatus.INTERNAL_ERROR,
                        error_message=f"Judge0 execution service unavailable (HTTP {resp.status_code})",
                    )

                if resp.status_code not in (200, 201):
                    logger.error("Judge0 submission failed: %s %s", resp.status_code, resp.text)
                    return ExecutionResult(
                        status=ExecutionStatus.INTERNAL_ERROR,
                        error_message=f"Judge0 submission rejected (HTTP {resp.status_code})",
                    )

                data = resp.json()
                token = data.get("token")
                if not token:
                    return ExecutionResult(
                        status=ExecutionStatus.INTERNAL_ERROR,
                        error_message="Judge0 did not return a submission token",
                    )

                # Poll with bounded backoff
                return await self._poll_result(client, token)

        except httpx.TimeoutException:
            return ExecutionResult(
                status=ExecutionStatus.INTERNAL_ERROR,
                error_message="Connection to Judge0 timed out during submission",
            )
        except httpx.HTTPError as e:
            logger.error("Judge0 HTTP connection error: %s", str(e))
            return ExecutionResult(
                status=ExecutionStatus.INTERNAL_ERROR,
                error_message=f"Judge0 connection error: {type(e).__name__}",
            )

    async def _poll_result(self, client: httpx.AsyncClient, token: str) -> ExecutionResult:
        """Poll Judge0 for submission result with bounded exponential backoff."""
        delay = self.settings.judge0_poll_interval
        max_poll_time = self.settings.judge0_max_poll_time
        max_delay = 4.0
        elapsed = 0.0

        while elapsed < max_poll_time:
            await asyncio.sleep(delay)
            elapsed += delay

            try:
                resp = await client.get(
                    f"{self.base_url}/submissions/{token}?base64_encoded=false&fields=status_id,status,stdout,stderr,exit_code,time,memory,compile_output,message",
                    headers=self._headers(),
                )

                if resp.status_code == 429:
                    delay = min(delay * 1.5, max_delay)
                    continue

                if resp.status_code in (500, 502, 503, 504):
                    logger.warning("Judge0 poll returned %s, retrying...", resp.status_code)
                    delay = min(delay * 1.5, max_delay)
                    continue

                if resp.status_code != 200:
                    logger.warning("Judge0 poll returned unexpected %s", resp.status_code)
                    return ExecutionResult(
                        status=ExecutionStatus.INTERNAL_ERROR,
                        error_message=f"Judge0 poll error (HTTP {resp.status_code})",
                    )

                data = resp.json()
                # Status can be returned as status_id (int) or status.id (dict)
                status_id = data.get("status_id")
                if status_id is None and isinstance(data.get("status"), dict):
                    status_id = data.get("status", {}).get("id")
                status_id = status_id or 0

                # 1 = In Queue, 2 = Processing
                if status_id in (1, 2):
                    continue

                # Finished execution — map result
                exec_status = _map_judge0_status(status_id)
                stdout = data.get("stdout") or ""
                stderr = data.get("stderr") or ""
                compile_output = data.get("compile_output") or ""
                message = data.get("message") or ""

                if exec_status == ExecutionStatus.COMPILATION_ERROR:
                    stderr = compile_output or stderr or message
                elif exec_status == ExecutionStatus.RUNTIME_ERROR and not stderr:
                    stderr = message

                return ExecutionResult(
                    status=exec_status,
                    stdout=stdout.strip(),
                    stderr=stderr.strip(),
                    exit_code=data.get("exit_code"),
                    time_seconds=float(data["time"]) if data.get("time") else None,
                    memory_kb=data.get("memory"),
                    error_message=message if exec_status == ExecutionStatus.INTERNAL_ERROR else "",
                )

            except httpx.TimeoutException:
                delay = min(delay * 1.5, max_delay)
                continue
            except Exception as e:
                logger.error("Error during Judge0 polling: %s", str(e))
                return ExecutionResult(
                    status=ExecutionStatus.INTERNAL_ERROR,
                    error_message=f"Judge0 polling error: {type(e).__name__}",
                )

        return ExecutionResult(
            status=ExecutionStatus.TIMEOUT,
            error_message="Judge0 polling deadline exceeded",
        )

    async def is_healthy(self) -> bool:
        """Check if direct Judge0 CE is reachable."""
        try:
            async with httpx.AsyncClient(timeout=self.settings.judge0_request_timeout) as client:
                resp = await client.get(
                    f"{self.base_url}/statuses",
                    headers=self._headers(),
                )
                return resp.status_code == 200
        except Exception:
            return False


# Singleton provider
_provider: Optional[Judge0ExecutionProvider] = None


def get_execution_provider() -> Judge0ExecutionProvider:
    """Get the singleton execution provider."""
    global _provider
    if _provider is None:
        _provider = Judge0ExecutionProvider()
    return _provider


async def verify_judge0_endpoint() -> dict:
    """Utility to test and verify the configured direct Judge0 CE endpoint."""
    provider = get_execution_provider()
    healthy = await provider.is_healthy()
    lang_id = await provider.get_language_id() if healthy else None
    
    test_exec = None
    if healthy:
        try:
            res = await provider.execute("print('JUDGE0_VERIFIED')", timeout_seconds=5.0)
            test_exec = {
                "status": res.status.value,
                "stdout": res.stdout,
                "exit_code": res.exit_code,
            }
        except Exception as e:
            test_exec = {"error": str(e)}

    return {
        "base_url": provider.base_url,
        "is_healthy": healthy,
        "resolved_language_id": lang_id,
        "test_execution": test_exec,
    }

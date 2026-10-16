# Debug Dojo — Security Model & Invariants

Debug Dojo is designed to prevent cheating, solution leaks, and sandbox escapes while maintaining a safe, progressive learning environment.

---

## 1. Hidden Test Protection & Zero Leakage

### Invariants
1. **Never in API Responses**: Hidden test fixtures (inputs and expected outputs) are never returned in public or authenticated API endpoints (`/api/challenges`, `/api/challenges/{id}`, or `/api/submit`).
2. **Never in Frontend Code**: The client bundle does not include hidden test values or answers.
3. **Never in AI Prompts**: Prompts to the Groq LLM include only high-level problem descriptions and visible test outcomes. Hidden inputs/outputs are never passed to the LLM.
4. **Server-Side Evaluation**: Comparison between actual learner output and expected output occurs exclusively on the backend in `modules/judge/engine.py`.

### Adversarial Defenses
- **Harness Inspection**: The test harness generated for sandboxed execution evaluates `__result__ = fn(...)` and prints `repr(__result__)`. The expected output is never included in the harness script, preventing adversarial learner code from inspecting `globals()`, `locals()`, or Python frame stacks (`sys._getframe()`) to extract expected outputs.

---

## 2. Sandboxed Code Execution

- **Isolation**: Learner code is executed inside Direct Judge0 CE sandboxed containers (via `https://ce.judge0.com` or self-hosted instances), never within the FastAPI web process.
- **Direct Auth**: Communicates directly with Judge0 CE without intermediary proxies (RapidAPI removed). Sends `X-Auth-Token` only when an API key is explicitly configured.
- **Resource Limits**:
  - CPU Time Limit: Configured via `JUDGE0_EXECUTION_TIMEOUT` (default 5.0 seconds)
  - Wall Time Limit: `JUDGE0_EXECUTION_TIMEOUT + 5.0` seconds
  - Memory Limit: 128 MB (128,000 KB)
  - Network Disabled: Container network namespace is isolated (`enable_network: false`).
- **Outcome Classification**:
  - `passed`: Actual output matches expected output.
  - `wrong_output`: Code executed without errors, but output differs from expected.
  - `runtime_error`: Uncaught exceptions, memory violations, or non-zero exit codes.
  - `timeout`: Code execution exceeded wall/CPU deadline.

---

## 3. Progressive Hints & Anti-Solution Guardrails

- **3-Tier Progressive Ladder**:
  1. *Conceptual Nudge*: Points to relevant Python concept areas without code.
  2. *Debugging Direction*: Points toward where the discrepancy might lie.
  3. *Specific Guidance*: Concrete advice without writing out the fix.
- **Automated Anti-Solution Filter**: Groq outputs are inspected before being sent to the learner. Any hint containing complete function definitions (`def ...`) or full code solution blocks is discarded in favor of deterministic fallback hints.

---

## 4. Authentication & Authorization

- **JWT Verification**: Handled via `modules/auth/dependencies.py` using Supabase JWT secret.
- **Ownership Enforcement**:
  - Submission records can only be accessed by the learner who submitted them.
  - Requesting hints on a submission requires ownership of that submission ID.
- **Cross-User Protection**: Attempts by user A to inspect user B's dashboard (`/api/learner/{learner_id}`) are rejected with HTTP 403 Forbidden.
- **Rate Limiting**: Protects execution and LLM endpoints against abuse (`10/min` on submit, `20/min` on hints via SlowAPI).

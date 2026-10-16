# Debug Dojo — Acceptance Checklist

## Challenge Bank
| # | Requirement | Status | Evidence |
|---|------------|--------|----------|
| 1 | 10+ original Python challenges | PASS | 12 challenges in `challenges/bank.py`, verified in `tests/test_challenges.py` |
| 2 | 3+ difficulty levels | PASS | `easy`, `medium`, `hard` in `challenges/bank.py`, verified in `tests/test_challenges.py` |
| 3 | 4+ concepts covered | PASS | lists, slicing, strings, iteration, math, recursion, edge-cases, dictionaries |
| 4 | `last-k-total` implemented correctly | PASS | Verified in `tests/test_challenges.py` against all test fixtures |
| 5 | `count-passes` implemented correctly | PASS | Verified in `tests/test_challenges.py` against all test fixtures |
| 6 | `first-n-squares` implemented correctly | PASS | Verified in `tests/test_challenges.py` against all test fixtures |
| 7 | `middle-three` implemented correctly | PASS | Verified in `tests/test_challenges.py` against all test fixtures |
| 8 | Each challenge has 3+ visible tests | PASS | Verified in `tests/test_challenges.py` (3 visible tests each) |
| 9 | Each challenge has 5+ hidden tests | PASS | Verified in `tests/test_challenges.py` (5-6 hidden tests each) |
| 10 | Curated hints for mandatory challenges | PASS | 3 progressive hints per challenge in `modules/hints/curated.py` |

## Judge Engine (Direct Judge0 CE)
| # | Requirement | Status | Evidence |
|---|------------|--------|----------|
| 11 | `passed` outcome works | PASS | Verified in `tests/test_judge.py::test_judge_outcome_passed` |
| 12 | `wrong_output` outcome works | PASS | Verified in `tests/test_judge.py::test_judge_outcome_wrong_output` |
| 13 | `runtime_error` outcome works | PASS | Verified in `tests/test_judge.py::test_judge_outcome_runtime_error` |
| 14 | `timeout` outcome works | PASS | Verified in `tests/test_judge.py::test_judge_outcome_timeout` |
| 15 | Output comparison is correct | PASS | Repr comparison & normalization in `tests/test_judge.py::test_output_comparison` |
| 16 | Each test runs in isolated execution | PASS | Verified in `tests/test_judge.py::test_judge_submission_isolated_execution` |
| 16a | Direct Judge0 CE headers & no RapidAPI | PASS | Verified in `tests/test_judge.py::test_judge0_direct_headers_no_rapidapi` (omits auth when key is empty, no RapidAPI headers) |
| 16b | Dynamic Python language discovery | PASS | Verified in `tests/test_judge.py::test_judge0_language_discovery` (discovers ID 92 for Python 3.11) |
| 16c | Distinction of service failures vs learner failures | PASS | Verified in `tests/test_judge.py::test_judge_distinguishes_service_failure_from_code_failure` & `tests/test_api.py::test_submit_returns_503_when_execution_service_unavailable` |
| 16d | Live Judge0 CE endpoint integration | PASS | Verified in `tests/test_judge.py::test_live_judge0_ce_endpoint` against `https://ce.judge0.com` |


## Hidden-Test Security
| # | Requirement | Status | Evidence |
|---|------------|--------|----------|
| 17 | Hidden inputs never in API responses | PASS | Verified in `tests/test_security.py::test_challenge_endpoints_never_include_hidden_tests` |
| 18 | Hidden expected outputs never in responses | PASS | Verified in `tests/test_security.py::test_submission_response_never_reveals_hidden_inputs_or_outputs` |
| 19 | Hidden values not in AI prompts | PASS | Verified in `tests/test_security.py::test_ai_prompts_never_contain_hidden_test_data` |
| 20 | Hidden values not in frontend code | PASS | Verified: only visible tests loaded in UI bundle; hidden tests report number/outcome only |
| 21 | Adversarial print-inputs test passes | PASS | Verified in `tests/test_security.py::test_adversarial_code_cannot_inspect_expected_output` |
| 22 | Adversarial inspect-globals test passes | PASS | Expected output omitted from harness; verified in `tests/test_security.py` |

## Authentication & Authorization
| # | Requirement | Status | Evidence |
|---|------------|--------|----------|
| 23 | Email/password sign-up works | PASS | Implemented in `frontend/src/pages/AuthModal.jsx` with Supabase Auth |
| 24 | Sign-in works | PASS | Implemented in `frontend/src/pages/AuthModal.jsx` |
| 25 | Sign-out works | PASS | Implemented in `frontend/src/components/Navbar.jsx` |
| 26 | Password recovery works | PASS | Implemented in `frontend/src/pages/AuthModal.jsx` |
| 27 | JWT verification on backend | PASS | Verified in `tests/test_api.py::test_auth_protection_on_endpoints` |
| 28 | Cross-user access rejected | PASS | Verified in `tests/test_api.py::test_cross_user_access_rejected` (HTTP 403) |
| 29 | Ownership enforced on submissions | PASS | Verified in `tests/test_api.py::test_submission_ownership_enforced_on_hints` (HTTP 403) |

## API Endpoints
| # | Requirement | Status | Evidence |
|---|------------|--------|----------|
| 30 | POST /api/submit works | PASS | Verified in `tests/test_api.py` and `tests/test_security.py` |
| 31 | POST /api/hint works | PASS | Verified in `tests/test_api.py` and `tests/test_hints.py` |
| 32 | GET /api/learner/{id} works | PASS | Verified in `tests/test_api.py` |
| 33 | Health endpoint works | PASS | Verified in `tests/test_api.py::test_health_endpoints` |
| 34 | OpenAPI docs generated | PASS | Verified in `tests/test_api.py::test_openapi_documentation_generated` |

## Hints & AI Coaching
| # | Requirement | Status | Evidence |
|---|------------|--------|----------|
| 35 | 3+ ordered hints per failure | PASS | Verified in `tests/test_hints.py::test_all_challenges_have_curated_hints` |
| 36 | Hints don't reveal solutions | PASS | Verified in `tests/test_hints.py::test_anti_solution_detector` |
| 37 | Groq integration with timeouts | PASS | Implemented in `modules/hints/groq_client.py` with 15s timeout and retries |
| 38 | Deterministic fallback hints | PASS | Verified in `tests/test_hints.py::test_deterministic_fallback_when_beyond_curated_and_ai_unavailable` |
| 39 | Hint ladder state persists | PASS | Verified in `tests/test_hints.py::test_hint_ladder_progression_and_persistence` |
| 40 | Adversarial hint-leakage test passes | PASS | Solution filtering in `groq_client.py` rejects code containing definitions or solution blocks |

## Mistake Detection & Learning
| # | Requirement | Status | Evidence |
|---|------------|--------|----------|
| 41 | 5 mistake categories implemented | PASS | Verified in `tests/test_diagnosis.py` (print_not_return, off_by_one, short_input, boundary, mutates) |
| 42 | Recurring = 2+ distinct challenges | PASS | Verified in `tests/test_diagnosis.py::test_recurring_mistakes_in_dashboard` |
| 43 | Mastery scoring works | PASS | Verified in `tests/test_learner.py::test_mastery_scoring_with_and_without_hints` |
| 44 | Recommendations with reasons | PASS | Verified in `tests/test_learner.py::test_recommendations_target_recurring_mistakes` |
| 45 | Progress persists across sessions | PASS | Persisted to `learner_profiles`, `submissions`, and `concept_masteries` |

## UI/UX
| # | Requirement | Status | Evidence |
|---|------------|--------|----------|
| 46 | Landing page | PASS | Implemented in `frontend/src/pages/LandingPage.jsx` |
| 47 | Auth flows (sign-up/in/out/recovery) | PASS | Implemented in `frontend/src/pages/AuthModal.jsx` |
| 48 | Learner dashboard | PASS | Implemented in `frontend/src/pages/DashboardPage.jsx` |
| 49 | Challenge catalogue with filters | PASS | Implemented in `frontend/src/pages/CataloguePage.jsx` |
| 50 | Coding workspace with CodeMirror | PASS | Implemented in `frontend/src/components/CodeEditor.jsx` (CodeMirror 6 Python) |
| 51 | Progressive hints panel | PASS | Implemented in `frontend/src/components/HintDrawer.jsx` |
| 52 | Debugging explanation panel | PASS | Implemented in `frontend/src/components/ResultsPanel.jsx` |
| 53 | Responsive design | PASS | Implemented in `frontend/src/styles/theme.css` |
| 54 | Loading/error/empty states | PASS | Handled across all pages and components |
| 55 | All controls functional | PASS | Navigation, filters, run, submit, reset, hint ladder fully wired |
| 56 | Keyboard accessible | PASS | `Mod-Enter` hotkey run shortcut, semantic inputs, modal accessibility |

## Deployment
| # | Requirement | Status | Evidence |
|---|------------|--------|----------|
| 57 | Frontend production build passes | PASS | `npm run build` succeeds in 1.91s with 0 errors |
| 58 | Backend starts successfully | PASS | FastAPI lifespan initializes tables, seeds challenges, all 48 pytest tests pass including live Judge0 CE integration |
| 59 | .env.example files complete | PASS | `backend/.env.example` and `frontend/.env.example` present |
| 60 | Deployment docs accurate | PASS | Detailed guides in `docs/DEPLOYMENT.md` and `docs/SECURITY.md` |

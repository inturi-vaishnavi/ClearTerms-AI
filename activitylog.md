# ClearTerms Activity Log

## Project goal

Build an AI-powered application that helps people understand privacy policies
and terms of service in plain English, with explanations grounded in the
original policy text.

## 2026-10-25 — Initial application foundation

- Changes: Added the initial Streamlit interface with a fictional sample policy,
  empty-input validation, and a temporary response for non-empty input. Added
  the dependency manifest, secret/cache exclusions, implementation checklist,
  and this activity log. Clarified in the README that AI analysis is not yet
  implemented.
- Files affected: `app.py`, `requirements.txt`, `.gitignore`,
  `implementation.md`, `activitylog.md`, and `README.md`.
- Verification: Python syntax parsing of `app.py` passed. The Streamlit app was
  not launched and no automated UI tests were run.
- Issues: The interface does not call an AI model or produce policy analysis.
  Dependencies have not been installed.
- Next steps: Create a virtual environment, install the requirements, launch
  the app, then implement and test the MVP Gemini/Gemma integration following
  `implementation.md`.

## 2026-10-25 — UI polish

- Changes: Set the page icon to the supported notebook emoji. Confirmed the
  empty-input message reads naturally as requested; app behavior, sample
  policy, labels, and layout remain unchanged.
- Files affected: `app.py` and `activitylog.md`.
- Verification: Python syntax parsing and static checks for the page icon and
  validation message passed. `git diff --check` passed. The app has not been
  launched.
- Issues: No UI behavior has been tested in a running Streamlit session.
- Next steps: Launch the app locally to visually verify the icon and manually
  exercise the empty-input message.

## 2026-10-25 — Add isolated policy analysis backend

- Changes: Added a separate Google Gen AI SDK backend with environment-based
  credentials and model configuration, input limits, structured response
  validation, verbatim evidence checks, safe exceptions, and a missing-text
  caveat. Added mocked unit tests, a placeholder-only environment example, and
  updated the dependency manifest, ignore rules, README status, and
  implementation checklist. The backend is not connected to the Streamlit UI.
- Files affected: `analyzer.py`, `tests/test_analyzer.py`, `requirements.txt`,
  `.gitignore`, `.env.example`, `implementation.md`, `activitylog.md`, and
  `README.md`.
- Verification: `python -m unittest discover -s tests -v` passed all 9 mocked
  unit tests. Python syntax checks and `git diff --check` passed; ignore-rule
  checks confirmed `.env` and virtual environments are ignored while
  `.env.example` is not. No packages were installed and no live Gemini API
  request was made.
- Issues: The configured default model and live request compatibility have not
  been verified against the Gemini API. The UI does not call the backend.
- Next steps: Run the mocked unit tests in the project's Python environment,
  verify the selected model with the live API, then integrate the backend into
  the UI in a separate task.

## 2026-10-25 — Build policy analysis experience

- Changes: Restyled the Streamlit app with a forest-green and pale-green
  responsive layout. Connected the existing `analyze_policy` function to the
  Analyze Policy action, preserved the sample selector and empty-input check,
  and rendered backend summaries, status counts, findings, and verified
  evidence excerpts. Added safe display of backend errors and an
  informational-only disclaimer. No mock findings, scores, or legal
  conclusions were added.
- Files affected: `app.py`, `implementation.md`, `activitylog.md`, and
  `README.md`.
- Verification: `python -m unittest discover -s tests -v` passed all 9 mocked
  backend tests. Python syntax parsing, Pylance syntax validation, and
  `git diff --check` passed. With the existing `.venv` (Streamlit 1.66.1),
  AppTest passed initial rendering, empty-input validation, sample selection,
  mocked analysis/evidence rendering, and safe API-error display. No packages
  were installed and no live Gemini API request was made.
- Issues: Live model compatibility and a real API-backed browser session remain
  unverified.
- Next steps: Verify the selected model with the live API, then run the app and
  manually review actual results against the supplied policy and its evidence.

## 2026-10-25 — Load API credentials from root dotenv file

- Changes: Added `python-dotenv` and load the repository-root `.env` before
  looking up `GEMINI_API_KEY`, preserving existing environment values with
  `override=False`. Added a regression test for root-file loading and
  environment-variable precedence. Documented `.env` setup without including
  credentials.
- Files affected: `analyzer.py`, `requirements.txt`, `tests/test_analyzer.py`,
  `README.md`, and `activitylog.md`.
- Verification: `python -m unittest discover -s tests -v` passed all 10 tests.
  Pylance syntax validation and `git diff --check` passed. Confirmed `.env` is
  ignored and `.env.example` is not. Installed `python-dotenv` in the existing
  project virtual environment to run the tests; no key was displayed.
- Issues: A live Gemini API request was not made.
- Next steps: Run ClearTerms with the configured `.env` and confirm a live
  request succeeds using the selected model.

## 2026-10-25 — Harden model JSON response handling

- Changes: Configured the Google Gen AI SDK request for JSON output using a
  schema that matches the existing result structure. The parser now accepts
  surrounding whitespace and a standalone Markdown JSON fence, while rejecting
  surrounding prose, missing or extra fields, invalid statuses, and
  unverifiable evidence. Added regression coverage for the reported fenced
  JSON failure and malformed variants.
- Files affected: `analyzer.py`, `tests/test_analyzer.py`, `implementation.md`,
  and `activitylog.md`.
- Verification: `python -m unittest discover -s tests -v` passed all 16 tests.
  The installed SDK accepted the structured JSON config; `git diff --check`
  passed. No live Gemini API request was made.
- Issues: Compatibility of structured JSON output with the configured live
  Gemma model has not been verified; no repeated API requests were made.
- Next steps: Verify one live request when ready, then assess whether the
  configured model supports the SDK JSON schema request.

## 2026-10-25 — Temporary model selection (superseded)

- Changes: Temporarily changed the default to a non-Gemma model. This choice
  was incorrect for ClearTerms' Gemma-only requirement and is superseded by the
  entry below.
- Files affected: `analyzer.py`, `.env.example`, `tests/test_analyzer.py`,
  `implementation.md`, `README.md`, and `activitylog.md`.
- Verification: `python -m unittest discover -s tests -v` passed all 16 tests.
  Pylance syntax validation and `git diff --check` passed. No live API request
  was made.
- Issues: The selected model violated the Gemma-only requirement.
- Next steps: Use the documented hosted Gemma model and verify access.

## 2026-10-25 — Restore Gemma-only hosted model

- Changes: Set the default and example model to
  `gemma-4-26b-a4b-it`. Reject configured model IDs that are not Gemma. Updated
  tests and documentation to make the Gemma-only choice explicit. Kept
  `GEMINI_API_KEY` as the SDK-required environment variable name.
- Files affected: `analyzer.py`, `.env.example`, `tests/test_analyzer.py`,
  `README.md`, `implementation.md`, and `activitylog.md`.
- Verification: One minimal live request to `gemma-4-26b-a4b-it` using the
  existing API key and JSON schema configuration returned non-empty output;
  neither the response body nor the key was printed. This verifies access, not
  the response's JSON conformance. `python -m unittest discover -s tests -v`
  passed all 17 tests; `git diff --check` passed.
- Issues: A full policy analysis request was not made; policy extraction and
  evidence accuracy have not been verified live.
- Next steps: Verify full analysis output and evidence against policy input
  with a future, explicitly authorized live test.

## 2026-10-25 — Improve evidence excerpt verification

- Changes: Clarified the prompt to request short, contiguous excerpts copied
  from the untrusted policy text. Evidence matching now tolerates whitespace
  differences and canonical Unicode equivalence while returning the exact
  original source slice. Added one corrective model retry for evidence
  validation failures; unsupported excerpts remain rejected.
- Files affected: `analyzer.py`, `tests/test_analyzer.py`, and `activitylog.md`.
- Verification: The system `python -m unittest discover -s tests -v` command
  could not import the tests because `python-dotenv` is not installed in that
  interpreter. Running the suite with the project's `.venv` Python passed all
  20 tests. `git diff --check` passed. No live model requests were made.
- Issues: A live model response with the originally reported excerpt was not
  available for reproduction; coverage verifies raw-substring rejection,
  harmless formatting normalization, and the bounded retry behavior.
- Next steps: Manually verify evidence quality against real model output when
  a live request is explicitly authorized.

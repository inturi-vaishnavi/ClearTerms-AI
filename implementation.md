# ClearTerms Implementation Checklist

The initial interface is in place. The remaining tasks below prioritize a
realistic two-hour MVP; time estimates are approximate and intended to keep the
first working analysis small and reviewable. Items marked **Optional** are not
required for that MVP.

## Project setup

- [x] Create the initial Streamlit entry point and list its required dependency.
- [x] Ignore virtual environments, Python caches, environment files, and local
      secret files.
- [ ] [MVP — 5 min] Create a local virtual environment and install the listed
      dependencies.
- [ ] [MVP — 5 min] Confirm Python and Streamlit versions in the development
      environment.

## User interface

- [x] Show the ClearTerms title, tagline, and a short plain-English introduction.
- [x] Provide a large text area for pasted policy text.
- [x] Add a clearly labelled fictional sample policy to make the interface easy
      to try.
- [x] Preserve empty-input validation and call the analysis backend for
      non-empty input.
- [x] Add a loading state and a findings area for backend results.
- [x] Apply the responsive green palette, rounded cards, and summary layout.
- [x] Display backend summaries, status counts, explanations, and evidence
      without hardcoded findings or an overall risk score.

## Gemma model integration

- [x] Read `GEMINI_API_KEY` from the environment without hardcoding or printing
      it; provide a placeholder-only `.env.example`.
- [x] Use the hosted Gemma model `gemma-4-26b-a4b-it` through the Google Gen AI
      SDK and verify model access with one minimal request.
- [x] Add the Google Gen AI SDK dependency and a small, separately testable
      backend API-call function in `analyzer.py`.
- [x] Read `GEMINI_API_KEY` and `CLEARTERMS_MODEL` from environment variables,
      defaulting to `gemma-4-26b-a4b-it`; reject non-Gemma model IDs.
- [ ] [Optional] Add configurable model selection and usage/cost controls.

## Policy analysis and structured output

- [x] Prompt for concise, structured, plain-English output based only on the
      supplied policy text.
- [ ] [MVP — 15 min] Extract data-collection, third-party-sharing,
      data-retention, and account-deletion clauses or explicitly report when
      the policy does not state them.
- [x] Validate required response fields, statuses, finding types, and evidence
      excerpts against the supplied source text.
- [x] Request SDK structured JSON output with the existing response shape and
      safely parse whitespace-wrapped or standalone Markdown JSON fences.
- [x] Include a caveat that missing text does not prove a practice does not
      exist.
- [x] Connect the existing backend response schema to the UI without changing
      its fields.
- [ ] [MVP — 15 min] Test full policy analysis categories and evidence quality
      and JSON conformance against a live Gemma response.
- [ ] [Optional] Add additional clause categories and user-selectable analysis
      depth.

## Evidence and explanations

- [x] Show verified original policy excerpts beside each returned explanation.
- [x] Explain when no excerpt is available, and preserve the backend caveat
      about findings absent from the supplied text.
- [ ] [Optional] Add links from each result to its location in the pasted text.

## Error handling and security

- [x] Reject empty or whitespace-only input with a helpful message.
- [x] Handle malformed output, unsupported evidence, missing API keys, API
      failures, and oversized input with safe exceptions.
- [x] Enforce a 100,000-character policy input limit.
- [x] Exclude `.env`, `.env.*`, and common virtual environments while allowing
      `.env.example` to be committed.
- [ ] [MVP — 5 min] Verify that no real API keys or other secrets are committed.
- [x] Display an informational-only disclaimer and remind users to check
      important details against the complete policy.
- [ ] [Optional] Add rate limiting, request timeouts, and retry behavior where
      supported by the selected SDK.

## Testing

- [x] Add mocked unit tests for empty and whitespace-only input, oversized
      input, missing API key, malformed output, supported and unsupported
      evidence, safe API failures, model configuration, fenced JSON, missing
      fields, invalid statuses, and extraneous response content.
- [x] Run the mocked unit tests without making live model requests or installing
      packages.
- [x] Exercise the Streamlit empty state, input validation, sample selector,
      mocked analysis rendering, and safe service-error display with AppTest.
- [ ] [MVP — 10 min] Test legitimate, suspicious, and ambiguous fictional
      policies against a verified live model; check that explanations are
      grounded in supplied evidence.
- [ ] [MVP — 5 min] Run the app locally and verify the complete paste-to-results
      flow.

## Documentation and open-source release

- [x] Preserve the existing project description and document the current
      backend integration and remaining live-model limitation.
- [x] Record the initial implementation, verification, limitations, and next
      steps in `activitylog.md`.
- [x] Add `.env.example` with placeholder configuration values only.
- [x] Document that the UI calls `analyze_policy(policy_text)` and displays
      only backend-provided findings.
- [ ] [MVP — 5 min] Update README.md with the verified setup, run, and current
      feature instructions after integration is implemented.
- [ ] [MVP — 5 min] Add an appropriate open-source LICENSE after confirming the
      project's intended license.
- [ ] [MVP — 5 min] Verify that no API keys or other secrets are committed.
- [ ] [Optional] Add contribution guidelines and issue templates.

## Final demo and submission

- [ ] [MVP — 5 min] Run the app from a clean environment using documented
      commands.
- [ ] [MVP — 5 min] Demonstrate a fictional sample policy and an empty-input
      error.
- [ ] [MVP — 5 min] Review the output against the original evidence and explain
      known limitations during the demo.
- [ ] [Optional] Capture screenshots and prepare a short project demo.

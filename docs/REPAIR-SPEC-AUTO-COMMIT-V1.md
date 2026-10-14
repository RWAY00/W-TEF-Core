# W-TEF-Core Automation Repair Specification v1

Status: Draft for branch validation
Scope: `monitor.py`, `automation/v2/monitor_integration.py`, `automation/v2/auto_commit.py`, and the relevant GitHub Actions workflow.
Default branch: `main` (must not be modified directly by this repair).

## Goals

1. Generate one identifiable monitor JSON output per run.
2. Pass the exact output path through the integration layer; do not silently substitute another file.
3. Make dry-run the default and ensure it cannot write to GitHub.
4. Permit archival only after explicit opt-in and successful validation.
5. Report failure with a non-zero exit status; never turn a failed upload/push into a success.
6. Keep a traceable run record without exposing credentials or fabricating scientific validity.

## Mode contract

### Dry-run (default; `DO_COMMIT=no`)

- Generate the local monitor output.
- Validate that the output exists, is non-empty, parses as JSON, and has the expected minimum fields.
- Pass the exact generated path to the integration/archival script.
- Print the planned archival target and validation result.
- Do not call GitHub write APIs, create commits, push, or modify `main`.
- Return non-zero if generation or validation fails.

### Commit/archival mode (explicit opt-in; `DO_COMMIT=yes`)

- Require explicit mode from the workflow input and validate the output before any write.
- Archive the exact validated output, not an unrelated synthetic run log.
- Use a dedicated automation branch or a reviewable pull request; never write directly to `main` as part of this repair.
- Do not fall back to unauthenticated writes or silently swallow HTTP, git, or permission errors.
- Verify the archived path/content or commit result before reporting success.
- Keep tokens in the runner's secret environment only; never print tokens or authorization headers.
- If any precondition fails, stop and return non-zero. Do not label the run as archived.

## Output archival policy

- Canonical local output directory: `automation/v2/outputs/`.
- Each output is immutable and timestamped; do not overwrite a previous output.
- Archive only the exact output produced by the current run.
- Generated output files are not to be committed to `main` by this repair. Any future promotion to the permanent archive requires a separately reviewed policy.
- Keep the existing `WTEF_Daily_Log.json` semantics unchanged until its relationship to the monitor output is confirmed.
- Scientific metrics in `monitor.py` are illustrative placeholders at present; they must not be described as measured or validated scientific results.

## Validation checklist

- Default mode is dry-run even when the mode input is missing or malformed.
- Dry-run produces a valid local JSON file and performs no network write.
- Missing, empty, invalid JSON, or wrong-path input fails closed.
- Commit mode is blocked unless explicitly enabled.
- Commit mode archives the exact input file and verifies the result.
- Network/authentication failures produce a failed run, not a success message.
- Tests use temporary files or mocks and do not require a real PAT or write to `main`.
- Review the Git diff and all tests before any pull request/merge.

## Out of scope

- Changing W-TEF scientific equations or scientific claims.
- Changing the meaning of existing stability metrics.
- Public deployment or enabling new scheduled execution.
- Merging this branch into `main` without human review.

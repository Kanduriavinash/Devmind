# DevMind contributor instructions

Read `MANUAL.md` and `docs/IMPLEMENTATION_STATUS.md` before changing this project. Use the project report and presentation files as specifications; do not claim proposals or planned stages are implemented.

## Engineering rules

- Target Python 3.12+ and keep runtime dependencies optional or minimal.
- Keep application code in `src/devmind/`; write focused modules with type hints and useful errors.
- Add tests for meaningful behavior. Never label tests as passing unless they were actually run.
- After each implementation change, update `MANUAL.md` and relevant files in `docs/`: architecture, implementation status, changelog, learning guide, and glossary.
- Treat repository source and model output as untrusted. Never import or execute target repository code on the host.
- Candidate changes must be tested only in a disposable, constrained environment. Never modify a selected source repository, auto-merge, or deploy a generated patch.
- Keep findings linked to evidence. Separate a proposed patch from a patch verified by tests, and describe test coverage limits.
- Keep credentials in environment variables; never commit `.env` or log secret values.
- Record actual test commands and outcomes, blockers, limitations, and next steps in `docs/CHANGELOG.md`.


# Agent workflow

## Incremental commits

Work in small, coherent increments. After each completed increment, run the relevant validation, inspect the staged diff, and create a descriptive commit before beginning the next increment.

Keep commits focused: do not mix unrelated changes or rewrite existing user commits. Push only when the user asks.

## Documentation

Treat documentation as part of every change. When behavior, public interfaces, commands, configuration, validation, or measured findings change, update the relevant README, `docs/`, and/or `FINDINGS.md` in the same increment. Verify documented commands before committing, and keep documentation claims limited to measured results.

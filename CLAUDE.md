# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**canary** is an early warning agent — a monitoring/alerting system designed to detect issues before they escalate.

## Repository Structure

The intended layout (currently scaffolded with placeholders):

```
src/
  agents/    # Agent definitions and orchestration logic
  core/      # Core domain logic and data models
  skills/    # Reusable agent capabilities/skills
  tools/     # Tool integrations (APIs, external services)
  utils/     # Shared utilities
config/      # Configuration files
templates/   # Prompt or output templates
tests/       # Test suite
examples/    # Example usage and demos
docs/        # Documentation
```

> Note: All source files are currently placeholders. Update this file as the codebase is built out — especially with build/test commands, key architectural decisions, and any non-obvious conventions introduced.

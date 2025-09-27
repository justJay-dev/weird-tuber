# AI coding instructions — repo-specific notes

Purpose: provide concise, actionable guidance for automated coding agents working in this repository.

Core rules (do not remove):

-   NEVER write docstrings or comments unless explicitly requested.
-   NEVER edit `README.md` — this repository treats the README as a human-maintained artifact.
-   NEVER add documentation files or free-form markdown. Prioritize implementing code and tests when asked.
-   All new file names must use `snake_case` (example: `new_module.py`, `data_asset.csv`).

What this repository contains (discoverable):

-   Top-level `assets/` folder with image assets: `assets/avatar.png`, `assets/top.png`, `assets/bottom.png`.
-   No language-specific source code, build configuration, or package manifests (e.g., `package.json`, `pyproject.toml`, `src/`) were present during analysis.

Conventions & patterns observed:

Developer workflow notes (based on current repository state):

-   No automated build/test commands are discoverable. Before introducing CI, toolchains, or language choices, open an issue or include a clear note in your PR explaining the choice.

When to ask a human maintainer first:

-   Adding or changing `README.md` or other repo-level documentation.
-   Introducing a language/runtime or CI configuration (for example, adding Node or Python tooling).
-   Renaming or removing existing assets in `assets/`.

If you need more context, request the maintainer provide the intended runtime and any hidden workflows.

Please request feedback if any guidance here is unclear or incomplete.

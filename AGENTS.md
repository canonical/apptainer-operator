## Overview

This project is the `apptainer` charm, a subordinate Juju machine charm that
automates the full lifecycle of the [Apptainer](https://apptainer.org)
container runtime on Charmed HPC nodes. The charm installs and removes the
`apptainer` package (along with its supporting packages) on the machine of
the principal charm it is integrated with, applies the AppArmor profile
required for unprivileged user namespaces, and publishes OCI runtime data to
`slurmctld` through the `oci-runtime` integration. Source lives in `src/`;
unit tests in `tests/unit/`; BDD integration tests in `tests/integration/`;
a CC008-compliant Terraform module in `terraform/`.

The source layout is:

```text
.
├── src
│   ├── charm.py                     # Entrypoint; defines ApptainerCharm
│   ├── apptainer.py                 # Workload manager (ApptainerManager)
│   └── constants.py                 # Integration names
├── terraform                        # CC008-compliant Terraform module
└── tests
    ├── unit
    │   ├── conftest.py              # mock_charm fixture (ops.testing.Context)
    │   ├── test_apptainer.py
    │   └── test_charm.py
    └── integration
        ├── constants.py             # Feature file paths
        ├── mod.just                 # gherkinator recipes (validate/generate/diff)
        ├── test_edge.py             # BDD step definitions
        ├── features                 # Auto-generated Gherkin feature files
        └── plans                    # gherkinator YAML test plans
```

The project uses:

- `uv` for dependency management and packaging.
- `just` as the task runner (see `justfile`).
- `ruff` for formatting and linting, `codespell` for spell checking.
- `pyright` for static type checking.
- `ops` and `charmed-hpc-libs` for charm primitives.
- `charmed-slurm-oci-runtime-interface` and
  `charmed-slurm-slurmctld-interface` for integration interface
  implementations (maintained in the
  [`canonical/slurm-charms`](https://github.com/canonical/slurm-charms)
  monorepo).
- `ops.testing` for unit tests; `coverage.py` with branch coverage on
  `src/**/*.py`.
- `jubilant` + `gherkinator` + `pytest-jubilant-bdd` for BDD integration
  tests.
- `charmcraft` (with the `uv` plugin) to build the charm.

### Supported versions

- **Base:** Ubuntu 26.04.
- **Runtime:** Python 3.12+.
- **Juju:** the charm `assumes` `juju`; integration tests require Juju and
  LXD.

## Architecture conventions

The charm currently uses a flat layout: event handlers are registered
directly in `charm.py` and all workload logic lives in `apptainer.py`. Keep
this structure for small, focused changes, but apply the observer design
pattern from specification UHPC010 where appropriate — for example, when
adding a new integration or when `charm.py` begins to accumulate handlers,
move them into observer classes under `src/integrations/` and
`src/operations/` rather than growing `charm.py` further.

1. **`charm.py` is the entrypoint.** `ApptainerCharm.__init__` instantiates
   the `ApptainerManager` workload manager, creates the `OCIRuntimeProvider`
   for the `oci-runtime` integration, and registers the `install`/`stop` and
   `slurmctld_connected` handlers with `framework.observe` — nothing else.
2. **Workload logic is standalone.** `ApptainerManager` (in `apptainer.py`)
   inherits from `AptLifecycleManager` and owns the `apptainer` apt lifecycle
   (install/remove/version, with `fuse2fs`, `squashfuse`, and `gocryptfs` as
   additional packages), the custom AppArmor profile that enables
   unprivileged user namespaces (written and reloaded on install, removed on
   `remove`), and the `executable_path` lookup. It must be usable outside
   the context of a charm.
3. **Integrations.** The charm provides `oci-runtime` (interface
   `slurm-oci-runtime`, wrapped by `OCIRuntimeProvider` from
   `charmed-slurm-oci-runtime-interface`) and requires `juju-info`. When
   `slurmctld` connects, the leader unit publishes `OCIRuntimeData` (runtime
   type and executable path) on the relation.
4. **Application config.** The charm currently defines no application config
   options in `charmcraft.yaml`. When config options are added, validate them
   with a frozen `pydantic.dataclasses.dataclass` in `config.py` and a
   `ConfigObserver` (UHPC 016) wired as `self.typed_config` in
   `ApptainerCharm.__init__`; validation failures should raise `StopCharm`
   and set a `BlockedStatus` when a handler loads config. Defaults live in
   `charmcraft.yaml`, not in the dataclass.
5. **Use `charmed-hpc-libs` primitives.** Prefer `AptLifecycleManager`,
   `systemctl`, `leader`, `StopCharm`, and the `refresh` decorator (see
   `_apptainer_status_check` in `charm.py`) over hand-rolled equivalents.
   Integration interface implementations come from
   `charmed-slurm-*-interface` packages, not vendored charm libraries.

## Code style

Follow PEP 8 and PEP 257, plus:

### Imports

Three groups, alphabetized (enforced by ruff's `I001` rule): standard
library, third-party (`ops`, `charmed_hpc_libs`,
`charmed_slurm_oci_runtime_interface`,
`charmed_slurm_slurmctld_interface`), first-party (charm modules such as
`charm`, `apptainer`, `constants`).

### Module naming

Flat module names — `charm.py`, `apptainer.py`, `constants.py`. If observer
packages are introduced (UHPC010), use `integrations/` and `operations/`
with `__init__.py` re-exporting the public observer classes. Do **not** use
the `_`-prefix convention; the public API of each module is its top-level
surface.

### Docstrings

Every public module, class, and function must have a PEP 257 docstring
(ruff's `D` rules enforce this; test files are exempt via per-file ignores).
Document `Args`, `Returns`, and `Raises` sections for non-trivial functions
in the house style of `apptainer-operator`'s `apptainer.py` module.

### Type annotations

All function signatures must have explicit type annotations. `just
typecheck` (pyright) validates them.

If a typing issue is found in production code (`src/`), STOP and
propose a resolution to the human-in-the-loop before editing production code:

1. Describe the issue, its location, and the impact.
2. Propose a concrete fix.
3. Ask whether to proceed with the proposed fix or to research alternative
   resolutions.

Do not edit production code until the user explicitly approves the fix.

### Avoid inline error handling

Use explicit `raise` statements and intermediate variables for error
handling rather than burying logic in one-liners or ternary expressions.
Expected exceptions (`AptError`, `FileNotFoundError`) must be caught,
logged, and converted into a `StopCharm` carrying a descriptive
`BlockedStatus` that points the operator at `juju debug-log` — do not let
raw exceptions leak out of event handlers or `apptainer.py`.

### Comments

Do __not__ add generic one-off comments throughout the main codebase. Do add
comments in test files to provide justifications for assertions, mocks, and
workarounds.

### License headers

Every new source file must carry the Apache 2.0 license header at the top,
with the copyright owner set to `Canonical Ltd.` and the year set to the
current year by default. External contributors may set the copyright owner
to the organization they are contributing on behalf of. When editing an
existing file whose copyright year is stale, extend the range (for example,
`2025` → `2025-2026`). See `CONTRIBUTING.md` for the exact header text.

## Build commands

```bash
just setup               # Create the uv dev environment (uv sync --extra dev).
just build               # Pack the charm with charmcraft -v pack.
just clean               # Remove coverage data, caches, build artifacts, *.charm.
just lock                # Regenerate uv.lock.
just upgrade             # Upgrade uv.lock with the latest dependencies.
just generate-token      # Export a Charmhub release token to .charmhub.secret.
```

## Testing

```bash
just check           # Run static checks (lint, typecheck).
just unit            # Run unit tests with a coverage report.
just integration     # Run BDD integration tests (requires Juju and LXD).
just test            # Run all test suites (unit + integration).
just test <target>   # Run a specific test target.
just fmt             # Format with ruff and apply auto-fixes.
just lint            # codespell + ruff check.
just typecheck       # Static type checking with pyright.
```

### Unit tests

Use `ops.testing.Context` (the `Harness` is deprecated) to drive the charm.
The `mock_charm` fixture in `tests/unit/conftest.py` provides the `Context`.
Mock the workload by patching `AptOpsManager` methods (`install`, `remove`,
`is_installed`, `version`) and the AppArmor side effects
(`apptainer._APPARMOR_PROFILE_PATH`, `apptainer.systemctl`) with
`pytest-mock` — never call real `subprocess`, `systemctl`, or `apt` code
from unit tests. Each `ApptainerCharm` event handler and each
`ApptainerManager` method must have dedicated unit tests.

### Integration tests

Integration tests are Behavior-Driven. Author YAML test plans under
`tests/integration/plans/`, then use the `gherkinator` just module to
validate the plans and generate the Gherkin `.feature` files consumed by
`pytest-jubilant-bdd`:

```bash
just gherkinator validate   # Validate the YAML test plans.
just gherkinator generate   # (Re)generate .feature files from the plans.
just gherkinator diff       # Check generated features match the plans.
```

`just integration` runs the generated scenarios with pytest. Custom step
definitions live in `tests/integration/test_edge.py`; reusable steps come
from `pytest-jubilant-bdd`. Integration tests require Juju and LXD.

### Coverage

The target is **85% branch coverage** on `src/**/*.py`.
Do __not__ write unit tests for code paths that are impossible to reach in
production.

## Terraform

The `terraform/` directory contains a CC008-compliant Terraform module that
allows the `apptainer` charm to be deployed via Terraform in addition to the
Juju CLI. When creating, reviewing, or restructuring this module, follow the
[create-charm-terraform-module SKILL.md](https://github.com/canonical/hpc-team/blob/main/.agents/skills/create-charm-terraform-module/SKILL.md)
— it codifies the required file structure (`README.md`, `providers.tf`,
`terraform.tf`, `main.tf`, `variables.tf`, `outputs.tf`), mandatory/optional
inputs and outputs, the README structure, versioning conventions (`tf-X.Y.Z`
for a co-located module), and validation (`terraform fmt` + `terraform
validate`).

Because `apptainer` is a subordinate charm, the `units` and `constraints`
variables **must not** be defined. The `requires` output (`juju-info`) and
the `provides` output (`oci-runtime`) **must** be present in `outputs.tf`.

## Development workflow

1. Implement charm logic in `src/` following the architecture conventions
   above — new workload operations go in `apptainer.py`; new event handlers
   go in `charm.py`, or in an observer class when applying UHPC010.
2. Write matching unit tests in `tests/unit/`.
3. Run `just unit` — ensure all tests pass and coverage meets the 85% branch
   coverage target.
4. Format: `just fmt`.
5. Lint: `just lint` (codespell + ruff). Fix all linter errors.
6. Typecheck: `just typecheck` (pyright). Fix all typing errors. If a typing
   issue is in production code, follow the human-in-the-loop protocol in the
   Code style section above.
7. If adding or changing BDD scenarios, edit the YAML plans under
   `tests/integration/plans/`, then run `just gherkinator validate` and
   `just gherkinator generate`. Commit both the updated plans and the
   regenerated `.feature` files. Running the tests with `just integration`
   requires Juju and LXD — you may be editing on a machine that does not
   have either available.
   1. Ask for explicit approval to run `just integration` if previous
      instructions do not explicitly state whether to run the integration
      tests or not.
   2. If in plan mode, explicitly ask the human-in-the-loop if they want to
      skip running the integration tests with `just integration`.
8. Repeat for each new or modified file.

Pipe the output of shell commands to either `head` or `tail` to capture
`stdout` and/or `stderr`.

Ask questions to the human-in-the-loop if you require additional context or
further information before beginning work on non-trivial tasks.

## Commit conventions

Use Conventional Commits prefixes for commit messages:

- `feat:` — New user-facing feature.
- `fix:` — Bug fix.
- `test:` — Add or modify tests only.
- `chore:` — Maintenance tasks (formatting, dependency updates, etc.).
- `docs:` — Documentation only.
- `refactor:` — Code change that neither fixes a bug nor adds a feature.
- `ci:` — CI/CD pipeline changes.

Scopes are allowed (for example, `chore(deps):`, `chore(fmt):`,
`feat(oci-runtime):`).

### Commit trailers

- Commits must be signed off (`Signed-off-by:` trailer) **by the human**.
  Agents must never add a `Signed-off-by:` trailer on the human's behalf.
- Agents must include an `Assisted-by:` trailer identifying the agent and
  model.
- Order trailers as: `Assisted-by:` first, then the human's
  `Signed-off-by:` last (added by the human).

Format:

    Assisted-by: AGENT_NAME:MODEL_VERSION[:MODEL_VARIANT]

- `AGENT_NAME`: The AI tool (for example, `opencode`).
- `MODEL_VERSION`: The specific model version used.
- `MODEL_VARIANT`: The variant of the model version used (for example,
  `low`, `medium`, or `high`). Optional.

Other rules:

- Commit messages must be ASCII only.
- Keep PRs small and focused.
- Maintain a linear git history.
- All pre-commit checks must pass.
- Do not create new commits or open pull requests unless you are explicitly
  granted approval by the human-in-the-loop.

### Constraints

- Do __not__ add new dependencies beyond what is already in
  `pyproject.toml` without approval.
- Do __not__ install anything with `apt` or `snap` on the development
  machine. The charm may install `apptainer` through `AptLifecycleManager`
  at runtime on the Juju unit — that is unrelated.
- Do __not__ run commands that require `sudo`.
- Do __not__ edit production code (`src/`) without explicit user approval
  when the change originates from a typing issue — propose the fix first
  and wait for approval (see the human-in-the-loop protocol above).
- All errors must be handled explicitly in Python code — no bare
  `subprocess.run(..., check=True)` or `systemctl(...)` calls outside a
  `try/except` that logs and raises a charm-appropriate error.

## Further information

- [Specification UHPC010 — Observer design pattern in HPC charms](https://github.com/canonical/hpc-specs/blob/main/specs/UHPC%20010%20-%20Observer%20design%20pattern%20in%20HPC%20charms/uhpc010.md)
- [Specification UHPC016 — Charm configuration observer](https://github.com/canonical/hpc-specs/blob/main/specs/UHPC%20016%20-%20Charm%20configuration%20observer/uhpc016.md)
- [Specification CC008 — Charm Terraform Standards](https://github.com/canonical/hpc-team/blob/main/.agents/skills/create-charm-terraform-module/SKILL.md)
- [`charmed-hpc-libs`](https://github.com/canonical/charmed-hpc-libs) — shared charm primitives (`AptLifecycleManager`, `systemctl`, `leader`, `StopCharm`, `refresh`).
- [`slurm-charms`](https://github.com/canonical/slurm-charms) — maintains the `charmed-slurm-oci-runtime-interface` and `charmed-slurm-slurmctld-interface` packages under `pkg/`.
- [Charmed HPC documentation](https://ubuntu.com/hpc/docs/latest)

# Tasks: chat-ui and local-runtime

Finished work: [tasks/app-shell.md](app-shell.md). Map: [docs/capability-map.md](../docs/capability-map.md).

`chat-ui` and `local-runtime` do not have specs yet. CU-01 and LR-01 write those specs. Implementation tasks for a module are added only after a human approves that spec. Those two branches can be open at the same time.

Backend CI does not wait on those specs. The package is already on `main`, and the jobs mirror the frontend gates.

## How to record completion

- **Id** is stable. `CU-01`, `LR-01`, and `CI-01` are never renumbered or reused.
- **Completed** is the date of the task commit, `YYYY-MM-DD`. Leave it blank until that commit exists.
- One pull request is one branch from the table. Cut it from `main`.
- Do not add chat-ui or local-runtime implementation tasks to the spec branches.

| PR | Branch | Ids | Module |
| --- | --- | --- | --- |
| 1 | `docs/chat-ui-spec` | CU-01 | chat-ui |
| 2 | `docs/local-runtime-spec` | LR-01 | local-runtime |
| 3 | `ci/backend-check` | CI-01–CI-06 | backend CI |

## CU-01: Write the chat-ui spec

**Id:** CU-01
**Completed:**

**Description:** Specify how the existing React page uploads a PDF and shows an answer with citations. The page today is a placeholder. The HTTP contract stays the one in [docs/SPEC-app-shell.md](../docs/SPEC-app-shell.md). This task does not change `src/frontend` or `src/backend`.

**Status:** open

**Acceptance criteria:**

- [ ] `docs/SPEC-chat-ui.md` states the objective, commands, project structure, code style, testing strategy, boundaries, and success criteria.
- [ ] The spec uses `POST /documents` and `POST /chat` as they are. It does not add a backend route.
- [ ] The fixture sentence remains `DemoMarker value is 10 units.`
- [ ] [docs/capability-map.md](../docs/capability-map.md) links this spec.

**Verification:**

- [ ] A human reviews the spec before any chat-ui implementation task is added.

**Dependencies:** AS-CPB

**Files likely touched:**

- `docs/SPEC-chat-ui.md`
- `docs/capability-map.md`
- `tasks/todo.md`

**Estimated scope:** Medium

## LR-01: Write the local-runtime spec

**Id:** LR-01
**Completed:**

**Description:** Specify Compose for Ollama, Qdrant, and the API, and a Minikube profile that uses the same images. Ollama stays on the host at `host.minikube.internal:11434` unless the spec chooses a different place and says why. This task does not add Compose files or a cluster manifest.

**Status:** open

**Acceptance criteria:**

- [ ] `docs/SPEC-local-runtime.md` states the objective, commands, project structure, code style, testing strategy, boundaries, and success criteria.
- [ ] The spec names how the API container gets `PROFILE=local` and the service URLs. It does not change the app-shell HTTP contract.
- [ ] A live stack is out of `make check`. The spec says which check runs it.
- [ ] [docs/capability-map.md](../docs/capability-map.md) links this spec.

**Verification:**

- [ ] A human reviews the spec before any local-runtime implementation task is added.

**Dependencies:** AS-CPB

**Files likely touched:**

- `docs/SPEC-local-runtime.md`
- `docs/capability-map.md`
- `tasks/todo.md`

**Estimated scope:** Medium

## CI-01: Select backend changes in the path filter

**Id:** CI-01
**Completed:** 2026-10-23

**Description:** Add a `backend` filter so the new jobs run when `src/backend` or the workflow files change, and skip when a pull request only touches docs or markdown. Follow the existing `frontend` filter in `.github/path-filters.yml`.

**Status:** done

**Acceptance criteria:**

- [x] `.github/path-filters.yml` has a `backend` filter covering `src/backend/**` and the workflow files that call the backend jobs.
- [x] A docs-only change does not select `backend`.

**Verification:**

- [x] The filter matches `src/backend/src/health_api/main.py`.
- [x] The filter does not match `tasks/todo.md`.

**Dependencies:** AS-CPB

**Files likely touched:**

- `.github/path-filters.yml`

**Estimated scope:** Small

## CI-02: Lint the backend on a pull request

**Id:** CI-02
**Completed:** 2026-10-23

**Description:** On a pull request to `main`, when the `backend` filter matches, run Ruff lint from `src/backend`. Install with `uv sync --frozen` and do not install the `local` group. Pin actions to a full SHA, the same way the frontend jobs are pinned.

**Status:** done

**Acceptance criteria:**

- [x] `ci-pr.yml` has a backend lint job that runs `uv run ruff check .` in `src/backend`.
- [x] The job uses Python 3.13 and does not pass `--group local` or `--all-groups`.
- [x] The job is listed in `pr_complete.needs`.

**Verification:**

- [x] `actionlint` accepts `.github/workflows/ci-pr.yml`.
- [x] A reviewer can see the job is skipped unless `backend` is in the changed paths.

**Dependencies:** CI-01

**Files likely touched:**

- `.github/workflows/ci-pr.yml`

**Estimated scope:** Small

## CI-03: Check backend formatting on a pull request

**Id:** CI-03
**Completed:**

**Description:** Add the format gate next to lint. It runs `uv run ruff format --check .` from `src/backend` after the same frozen sync.

**Status:** open

**Acceptance criteria:**

- [ ] `ci-pr.yml` has a backend format job that runs `uv run ruff format --check .` in `src/backend`.
- [ ] The job does not install the `local` group.
- [ ] The job is listed in `pr_complete.needs`.

**Verification:**

- [ ] `actionlint` accepts `.github/workflows/ci-pr.yml`.

**Dependencies:** CI-01

**Files likely touched:**

- `.github/workflows/ci-pr.yml`

**Estimated scope:** Small

## CI-04: Typecheck the backend on a pull request

**Id:** CI-04
**Completed:**

**Description:** `make check` includes pyright. The pull request gate runs `uv run pyright` from `src/backend` so CI is not weaker than the local check.

**Status:** open

**Acceptance criteria:**

- [ ] `ci-pr.yml` has a backend typecheck job that runs `uv run pyright` in `src/backend`.
- [ ] The job does not install the `local` group.
- [ ] The job is listed in `pr_complete.needs`.

**Verification:**

- [ ] `actionlint` accepts `.github/workflows/ci-pr.yml`.

**Dependencies:** CI-01

**Files likely touched:**

- `.github/workflows/ci-pr.yml`

**Estimated scope:** Small

## CI-05: Test the backend on a pull request and on main

**Id:** CI-05
**Completed:**

**Description:** Run pytest from `src/backend` on pull requests and again on `main`. Upload JUnit XML the way the frontend unit job uploads its report. Do not start Docker or install the `local` group.

**Status:** open

**Acceptance criteria:**

- [ ] `ci-pr.yml` runs `uv run pytest --junitxml=test-results/pytest.xml` in `src/backend` and uploads that file.
- [ ] `ci-main.yml` runs the same test command when `backend` changes.
- [ ] Both jobs are listed in `pr_complete.needs` and `main_complete.needs`.
- [ ] Neither job installs the `local` group.

**Verification:**

- [ ] `actionlint` accepts both workflow files.
- [ ] The pytest command does not select the `integration` marker.

**Dependencies:** CI-01

**Files likely touched:**

- `.github/workflows/ci-pr.yml`
- `.github/workflows/ci-main.yml`

**Estimated scope:** Medium

## CI-06: Build the backend package on a pull request and on main

**Id:** CI-06
**Completed:**

**Description:** The backend build is the package build, `uv build`, from `src/backend`. Run it on pull requests and again on `main`. This is not a container image and does not start Compose or Minikube.

**Status:** open

**Acceptance criteria:**

- [ ] `ci-pr.yml` runs `uv build` in `src/backend`.
- [ ] `ci-main.yml` runs `uv build` when `backend` changes.
- [ ] Both jobs are listed in `pr_complete.needs` and `main_complete.needs`.
- [ ] Neither job installs the `local` group.

**Verification:**

- [ ] `actionlint` accepts both workflow files.
- [ ] `uv build` from `src/backend` produces a wheel locally.

**Dependencies:** CI-01

**Files likely touched:**

- `.github/workflows/ci-pr.yml`
- `.github/workflows/ci-main.yml`

**Estimated scope:** Small

## CI-CP1: Backend CI is required

**Id:** CI-CP1
**Completed:**

- [ ] CI-01 through CI-06 are merged.
- [ ] A pull request that changes `src/backend` runs lint, format, pyright, pytest, and `uv build`.
- [ ] A push to `main` that changes `src/backend` runs pytest and `uv build`.
- [ ] Docs-only changes skip those jobs.
- [ ] The jobs use `uv sync --frozen` and do not install the `local` group.

## CU-CP1: chat-ui spec approved

**Id:** CU-CP1
**Completed:**

- [ ] CU-01 is merged.
- [ ] A human has approved `docs/SPEC-chat-ui.md`.
- [ ] Implementation tasks for chat-ui are added to this file only after that approval.

## LR-CP1: local-runtime spec approved

**Id:** LR-CP1
**Completed:**

- [ ] LR-01 is merged.
- [ ] A human has approved `docs/SPEC-local-runtime.md`.
- [ ] Implementation tasks for local-runtime are added to this file only after that approval.

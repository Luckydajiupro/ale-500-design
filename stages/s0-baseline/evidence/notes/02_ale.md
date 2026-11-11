# 02_ale. The ALE engine repository

Provenance. Snapshot at /Users/mac/Workspaces/ale-研究设计/ale-phase0-workspace-20261108/inputs-readonly/02_ale.
Copy of https://github.com/AgentsLastExam/ale.git, branch main, HEAD 73517c2eb097abe7974e9ec4de9819a02cd0ee81 (verified with git log) [code].
Paths in this note are repo-relative. Evidence tags: doc, code, inference, unknown.

## 1. Identity

- Purpose. ALE runs agents against isolated Tasks, verifies their work, and records the evidence needed to reproduce every result. README.md:1-4 [doc].
- The CLI advertises itself as the Agents' Last Exam evaluation orchestrator. packages/ale-run/src/ale/run/cli/main.py:43-44 [code]. The constitution names it the Agents' Last Exam orchestration and evaluation framework. docs/constitution.md:3-4 [doc].
- Built by the AgentsLastExam GitHub org. README.md:9 [doc]. Snapshot verified at HEAD 73517c2 with git log [code].
- This repo holds framework code and foundational images, not benchmark tasks. Task content lives in independent Task repositories. README.md:63-64 [doc].
- Versions. Root workspace package is ale-workspace 0.0.0, never published. pyproject.toml:2-4 [code]. The three real packages are ale-core 0.1.1, ale-run 0.1.1, ale-verify 0.1.1. packages/ale-core/pyproject.toml:2-5 and siblings [code].
- Python 3.12 or newer. pyproject.toml:5 [code]. .python-version holds pinned language version 3.12. [code].
- License. No LICENSE file exists in the tree (measured with find) and pyproject.toml has no license key. pyproject.toml:1-27 [code]. License is unknown [unknown].
- Packaging. A uv workspace with three members plus the never-published root. pyproject.toml:21-27 [code]. Markers for needs_docker, needs_kvm, needs_orchard, needs_gpu, needs_gui, needs_llm, needs_hf_gated and siblings describe the test taxonomy. pyproject.toml:47-62 [code].

## 2. Layout

Top-level tree at depth 3 [code, measured with find].

- docs/guides and docs/specs. Maintained specifications and guides [doc, README.md:52-61].
- images/base/container-ubuntu22, images/base/vm-ubuntu24, images/base/vm-windows10 [doc, images/README.md:5-9].
- images/builders/vm-materializer. Converts a VM OCI rootfs to qcow2 [doc, images/README.md:10-11].
- images/runtimes/qemu-runner. Runs a prepared qcow2 with QEMU/KVM [doc, images/README.md:12-13].
- packages/ale-core/src/ale/core. Public contracts and interfaces [code].
- packages/ale-run/src/ale/run. Orchestration, providers, harnesses, Gateway, CLI [code].
- packages/ale-verify/src/ale_verify. Sandbox-local verification library [code].
- scripts. bootstrap.sh, doctor.py, setup_macos.py [code].
- tests/{unit,conformance,integration,acceptance,fixtures} [doc, tests/README.md:3-8].
- Workflow files under .github/workflows/ci.yml, images.yml, task-check.yml [code].

Size. 467 files total, 10M including .git [code, measured with find -type f | wc -l and du -sh].
Python dominates. The file list across packages has 24 ale-core modules, about 50 ale-run modules, 7 ale-verify modules, 13 presets and 14 harness adapter packages [code, measured].
CI runs on ubuntu-latest plus self-hosted kvm and desktop runners. .github/workflows/ci.yml:24-151 [code].

## 3. CLI

Entry point. `ale = "ale.run.cli.main:main"` in packages/ale-run/pyproject.toml:11-12 [code]. Typer app with the root help Run, validate and author ALE evaluation tasks. packages/ale-run/src/ale/run/cli/main.py:42-74 [code].

How users run it. `git clone`, then `just bootstrap`, then `uv run ale --help`. README.md:8-13 [doc]. This is a uv workspace, not a pipx install [inference].

Commands and their job [code, main.py line refs].

- run (81). Runs a task or collection path and reports its verdict. Key flags: --agent, --model, --auth auto|api-key|subscription, --base-url, --api-key-env, --config TOML, --set key.path=value, --runs-dir, -n/--episodes, --episode-retries, --concurrency, --run-id, --no-resume, --require-reportable, --continue-from. The agent list names 14 CLIs plus computer-use, oracle and nop. main.py:81-157 [code].
- validate (176). Requires untouched all-zero and oracle full quality for every task, with fresh sandboxes. main.py:176-189 [code]. Semantics at docs/specs/episode-protocol.md:194-213 [doc].
- prepare (192). Builds or acquires task images, no sandbox. main.py:192-200 [code].
- reverify (203). Hidden internal authoring command. Re-runs separate verification against retained solver output without re-running setup or the agent. main.py:203-223 [code], docs/specs/episode-protocol.md:148-162 [doc].
- lint (226). Checks tasks from files alone, no container. main.py:226-241 [code].
- new-task (291). Scaffolds a task that passes ale lint immediately and solves itself. main.py:291-308 [code].
- vm-image push | pull (244-288). Publishes and acquires prebuilt VM disks through an OCI registry. [code].
- assets status | pull | push (311-372). Syncs task-local asset roots with same-named Hugging Face datasets. [code].
- sandbox list | destroy (382-407). Lists and removes retained sandboxes and snapshots. [code].

Lifecycle mapping. prepare builds images, validate proves feasibility, run measures agents, reverify re-scores, lint is the static half of admission [inference from docstrings].
No registry or classifier subcommand exists anywhere in the CLI tree [inference, grep of main.py].
Exit codes. Provider failures exit 4. main.py:56 [code]. Bad references use EXIT_BAD_REFERENCE from cli/tasks.py [code].
Quickstart credential model. `ALE_<PROVIDER>_API_KEY`, `ALE_<PROVIDER>_BASE_URL` in .env, or --base-url plus --api-key-env for one-off endpoints. README.md:15-30 [doc]. oracle and nop agents need no model credential. README.md:32-37 [doc].
Justfile recipes. bootstrap, doctor, wt, test, test-int, test-harnesses, test-vm, lint, fmt, images, demo. Justfile:19-82 [code].

## 4. New task format

One task is one self-contained folder. Nothing outside it affects it. docs/specs/task-authoring.md:3-7 [doc].

Folder shape [doc, task-authoring.md:18-34].

- task.toml. Task configuration.
- instruction.md. Instruction shown to the evaluated agent, used verbatim.
- environment/. The machine. Dockerfile (container or Linux VM), build.ps1 (Windows), build.sh (macOS), and optional setup/ with setup.sh|setup.ps1.
- tests/. Verification. test.sh|test.ps1, verify.py, optional Dockerfile for a separate verifier.
- solution/. solve.sh|solve.ps1, the known-good solution for validation.

Required files are task.toml, instruction.md, and the tests and solution entries for the Task OS. docs/specs/task-authoring.md:36-43 [doc].
Stage script names come from the Stage enum: setup.sh|setup.ps1, test.sh|test.ps1, solve.sh|solve.ps1. packages/ale-core/src/ale/core/task.py:59-69 [code].

Schema. `schema_version = "1.4+ale.1"` is required and must be exactly this value. This is Harbor task.toml schema 1.4 with ALE extensions. packages/ale-core/src/ale/core/taskspec.py:525 and :783-800 [code]. The conversion story is doc at docs/specs/task-authoring.md:9-14 [doc].

Top-level keys of task.toml, from the strict TaskConfig model. packages/ale-core/src/ale/core/taskspec.py:791-800 [code].

- schema_version. Literal "1.4+ale.1", required.
- artifacts. Outcome paths or globs with optional exclude.
- task. The identity table. Required.
- metadata. Free-form values, no runtime behavior.
- environment. The solver machine.
- agent. Account, budget, network, sudo, workdir.
- verifier. Budget, env, verification mode, optional separate environment.
- solution. Env for the oracle only.

Only schema_version and [task].name are required. Every other key has a default. Unknown keys fail. taskspec.py:788-789 [code], task-authoring.md:47-50 [doc].

The [task] table carries name (org/name TaskId), description, version, authors, keywords. packages/ale-core/src/ale/core/taskspec.py:567-576 [code].
[environment] carries os (linux|windows|macos), vm, docker_image, vm_image, vm_base, build_timeout_sec, cpus, memory_mb, storage_mb, gpus, gpu_types, env, skills_dir, mcp_servers. taskspec.py:653-687 [code].
[agent] carries user, timeout_sec, network_mode (no-network|allowlist|public), allowed_hosts, sudo, workdir. taskspec.py:689-720 [code].
[verifier] carries timeout_sec, env, environment_mode (shared|separate), environment. taskspec.py:747-772 [code].

Fields the parent brief listed that do not exist here. id, template_id, family, requires, experiments, difficulty, subject, cost. None of these keys exist in TaskConfig or anywhere in the repo. Task identity is the org/name only. Keywords and metadata are free text. [code, taskspec.py full-field scan] [inference].
There is no experiments concept. Verification declarations are file-level, not data tables. The tests directory plus tests entry is the whole experiment/grading declaration [inference].

Concrete examples.
tests/fixtures/tasks/subagent-smoke/task.toml:1-25 shows artifacts, [task] name and keywords, [environment] docker_image/cpus/memory_mb, [agent] user/timeout/network, [verifier] timeout [code].
tests/fixtures/tasks/macos-desktop-smoke/task.toml:1-24 shows os=macos with a pinned Tart OCI image vm_image and network_mode=public [code].
The scaffold. `ale new-task` writes task.toml, instruction.md, environment/Dockerfile, tests/test.sh, tests/verify.py, solution/solve.sh under org agentslastexam. packages/ale-run/src/ale/run/scaffold.py:14-65 [code].

## 5. Evaluator and grader

Verification is an ordinary task-owned program. ALE reads one JSON result after the program exits successfully. There is no scoring registry, automatic aggregation, callback, or required tool order. docs/specs/verification.md:3-5 [doc].

Reward schema. The verifier writes Harbor's reward file at /logs/verifier/reward.json (C:\logs\verifier\reward.json on Windows, /opt/ale/logs/verifier/reward.json on macOS). It is a flat JSON object whose values are numbers. reward must be finite, 0 through 1. docs/specs/verification.md:9-16 [doc]. The checked schema fixture requires only reward, a number with minimum 0 and maximum 1, and allows other fields. tests/fixtures/verification-result-v1.schema.json:5-15 [code].
Optional verification.json holds the complete nested result. reward is rounded to two decimals round-half-up (0.995 to 1.0) before use. docs/specs/verification.md:13-22 [doc].

The ale_verify library. checks return ordinary data with score, diagnostic, raw_value, evidence. write(result) atomically saves the reward files. judge(kind, name, prompt, output_schema, files, reference, trajectory, mcp_servers) returns a dictionary, kind llm or agent. packages/ale-verify/README.md:3-19 [doc], docs/specs/verification.md:46-87 [doc].
Judge calls resolve provider keys on the Host exactly as the Gateway does and leave llm-judge.jsonl / agent-judge.jsonl records. docs/specs/verification.md:129-171 [doc].
Agent Judge runs the configured pinned CLI as root. This exists for tasks that need an agent to review work. docs/specs/verification.md:100-112 [doc].

How the evaluator connects to task files. Verify uploads tests/ into a root-only staging directory (/opt/ale/tests on Linux, C:\ProgramData\ALE\tests on Windows), runs the OS entry as framework identity with open egress, and selects Python 3.12+ exposed as ALE_VERIFY_PYTHON. docs/specs/episode-protocol.md:113-130 [doc].
answers and reference. The old answers concept is absent. The closest is the Judge reference parameter, inline text. The answer key equivalent is solution/, uploaded only for the oracle. docs/specs/episode-protocol.md:73-77 [doc]. No tc.json exists anywhere in the repo. [inference, no matches].

Verdicts. Rewards are named floats (dict str to float) and ALE never aggregates them. packages/ale-core/src/ale/core/verdict.py:47-48 [code].
The terminal status set is closed: completed, agent_error, env_error, task_error, timeout, budget_exceeded, cancelled, refused. packages/ale-core/src/ale/core/verdict.py:19-45 [code].
The result record ResultRecord schema_version 2 holds episode_id, status, rewards, metrics, failure, started_at, finished_at, phases, sandboxes, continuation. packages/ale-core/src/ale/core/result.py:58-72 [code].

Per-episode records [doc, docs/specs/trace.md:3-16].

- trajectory.json. The ATIF v1.8 agent trajectory.
- trace.transport.jsonl. Gateway calls, executed by the Gateway only.
- trace.execution.jsonl. Framework phases and commands.
- result.json. Terminal status, named rewards, failure, timings.
- verification.json. The complete task-authored result.
- lock.json. Immutable provenance, the RunLock.

Run directory shape is runs/<run>/<episode>/ with attempts/1 archived on retry, and runs/<run>/ledger.db as a rebuildable projection. docs/specs/trace.md:196-208 [doc].

## 6. Providers

Two kinds of provider. The lexicon separates Sandbox Providers from Model providers. docs/specs/lexicon.md:8-11 [doc].

Sandbox backends [doc, packages/ale-run/src/ale/run/providers/README.md:3-10].

- docker.py. Local Docker containers.
- qemu.py. QEMU/KVM guest runner for VMs.
- daytona.py. Daytona cloud containers.
- orchard.py. macOS VMs on Orchard/Tart.

Selection is by image kind and OS in ProviderRegistry. macOS VMs are hardwired to Orchard; containers default Docker with an optional daytona setting; VMs go to QEMU. packages/ale-run/src/ale/run/providers/__init__.py:22-55 [code]. RETAINING_PROVIDERS are docker, qemu, daytona. providers/__init__.py:19 [code].

Model providers. The registry is a Literal in packages/ale-core/src/ale/core/config.py:156 [code].
anthropic, gemini, meta, moonshot, openai, qwen, xai, zai.
Dialects are anthropic, gemini, openai-chat-completions, openai-responses. config.py:158 [code]. Judge dialect adds no gemini. config.py:160 [code].
Gateway modules normalize each dialect and a proxy.py serves allowlisted non-model egress. packages/ale-run/src/ale/run/gateway/README.md:8-16 [doc]. Dialect routes and limit behavior table at gateway/README.md:32-41 [doc].

API keys. Keys live in the checkout .env, never in sandboxes. ALE_<PROVIDER>_API_KEY with optional ALE_<PROVIDER>_BASE_URL. .env.example lists all eight providers plus ALE_CLAUDE_CODE_OAUTH_TOKEN, ALE_DAYTONA_API_KEY, ALE_HF_TOKEN. [code]. load_env reads .env once at CLI start and an exported shell variable wins. cli/main.py:74-78 [code].
Sandboxes receive only a short-lived episode Gateway token. docs/specs/security.md:131-158 [doc].
Subscription auth. Claude Code uses ALE_CLAUDE_CODE_OAUTH_TOKEN. Codex and Grok keep checkout-local .ale/auth/<harness>/auth.json profiles, mode 0600. docs/guides/subscription-auth.md:9-42 [doc].
Harness presets. Each agent has one TOML preset under packages/ale-run/src/ale/run/presets naming agent, model, version, settings, and gateway.provider plus dialect. packages/ale-run/src/ale/run/presets/claude-code.toml:1-19 [code]. There is no central model catalog file beyond these presets [inference].

## 7. OS and runtime

Supported operating systems. linux (default), windows, macos. packages/ale-core/src/ale/core/taskspec.py:63-66 [code].
Linux runs as containers (ubuntu22 base) or VMs (vm = true builds a Dockerfile into a VM via the vm-materializer). Windows always runs as a VM with PowerShell stage entries. macOS is an ALE addition as a macOS VM with sh entries. docs/specs/task-authoring.md:138-156 [doc].
Base images. ghcr.io/agentslastexam/container-ubuntu22-base and vm-ubuntu24-base. The Windows 10 base is private and licensed. images/README.md:5-13 and :38-41 [doc].
Container usage. Docker only for Linux containers. Justfile and bootstrap use uv, scripts/doctor.py checks the tree. Justfile:19-40 [code]. Tests mark Docker, KVM, Orchard, GPU, GUI and LLM-dependent cases. pyproject.toml:47-62 [code].
GUI tooling. Desktop base images carry a desktop. Resolution is set per sandbox and checked via Cua Driver. packages/ale-run/src/ale/run/providers/README.md:57-67 [doc]. A built-in screen-control MCP server, cua-desktop, is selected at run level, not by a task. docs/specs/lexicon.md:41-42 [doc]. The computer-use harness is the policy-style desktop agent. packages/ale-run/src/ale/run/harnesses/README.md:23 [doc]. No Playwright appears in any dependency (typer, aiohttp, huggingface-hub, pyyaml, pydantic, fastjsonschema are the runtime deps). packages/ale-run/pyproject.toml:5-12 [code] [inference].
External services.

- Hugging Face for task assets push/pull and private datasets. docs/specs/task-assets.md referred by docs/README.md:11-13 [doc].
- OCI registries (ghcr.io) for engine images and vm-image push/pull. cli/main.py:244-288 [code].
- Daytona is a billable cloud sandbox backend needing ALE_DAYTONA_API_KEY. pyproject.toml:53 [code], .env.example [code].
- Orchard/Tart is a local macOS VM controller installed by scripts/setup_macos.py. providers/README.md:225-232 [doc].
- Model vendor APIs go only through the Host Gateway. Any mention of Supabase, S3, Postgres or beartype. None exist in this repo. Validation uses pydantic and fastjsonschema. packages/ale-core/pyproject.toml:6, packages/ale-verify/pyproject.toml:6-8 [code].

Internet access. The sandbox network is sealed during the agent phase. Default is no-network, reaching only the Gateway. allowlist admits declared hosts through a host-side CONNECT proxy. public is opt-in and requires [metadata].network_justification. Setup and verification run with open egress. docs/specs/security.md:15-66 and :67-129 [doc]. macOS Tasks must declare public because Orchard cannot enforce the other modes. docs/specs/task-authoring.md:200-203 [doc]. Gemini web tools are forwarded only under open network. gateway/README.md:64-66 [doc].

## 8. Categories and taxonomy

No classifier, no registry.json, no difficulty, cost, subject, or modality fields. Grep across all sources finds only a test taxonomy, a status taxonomy, and CLI input-modality settings for qwen/pi/forgecode. [code, measured].
Task identity is the TaskId org/name, a lowercase slug unique in its collection. docs/specs/lexicon.md:12 [doc].
Classification is descriptive text only. [task].description, .version, .keywords plus free-form [metadata]. packages/ale-core/src/ale/core/taskspec.py:567-576 and :796 [code].
The quality standard speaks of preserving the intended capability difficulty in prose, not as data. docs/specs/task-quality-standard.md:20-25 [doc].
Task collection means a directory holding several task folders. Selection accepts filesystem paths only. Remote task registries are not part of the standard contract, stated literally in packages/ale-run/src/ale/run/sources.py:31-39 [code]. Folder discovery lives in packages/ale-run/src/ale/run/tasksets/manifest.py:42-50 [code].
ALE datasets conventions. Task assets are optional ignored files in a task synced with a same-named Hugging Face dataset. The HF namespace defaults to agents-last-exam. packages/ale-run/src/ale/run/assets.py:33 [code]. The assets subcommand manages them. cli/main.py:311-372 [code].
Naming split. Task org in fixtures is agentslastexam (org/name) while the HF asset namespace is agents-last-exam. tests/fixtures/tasks/subagent-smoke/task.toml:11 vs packages/ale-run/src/ale/run/assets.py:33 [code] [inference].
For the 500-task program this means classification for machine, modality, difficulty and cost must live outside the task folder, because the engine defines no such schema. [inference].

## 9. Tools and environment for agents

No requires and no machine field. The environment table is the machine declaration itself. There is no dependency spec section beyond the image. [inference, taskspec.py].
No command_para and no safe command registry. Zero grep matches. Harnesses pin exact CLI versions and the sandbox enforces privileges instead of a command allowlist. [grep] [inference].
Skills. [environment].skills_dir names an absolute directory in the image holding one directory per skill. The harness copies its contents to the agent skills directory before the agent starts. docs/specs/task-authoring.md:381-390 [doc].
MCP. [[environment.mcp_servers]] declares stdio (a program in the image) or streamable-http servers with optional headers carrying ${NAME} references. taskspec.py:579-626 [code]. Credential headers must be references without defaults and need https off loopback. task-authoring.md:391-407 [doc].
Operator-run resources may add or replace task skills and MCP servers per run. They stay on the Host until upload. docs/specs/security.md:289-306 [doc].
cua-desktop is ALE's built-in screen-control MCP, opt-in at run level and never auto-injected. docs/specs/lexicon.md:41-42 [doc].
Privileges. The agent runs as the image-declared account, default user. sudo works exactly when the task declares [agent].sudo = true, and the provider grants or revokes the sudoers rule at every start. docs/specs/security.md:180-205 [doc].
All command and file transport goes through guestd, the in-sandbox guest service, never provider-specific code paths. docs/specs/lexicon.md:45 [doc].
Stepwise environment. The computer-use policy harness drives the framework-owned TaskEnv with reset and step actions. packages/ale-core/src/ale/core/env.py:83-101 [code]. Per-step reward is reserved and None because scoring happens in verify. env.py:20-23 [doc].

## 10. Cross-references

Harbor. The format is Harbor's task.toml schema 1.4, environment/, tests/, solution/. A field ALE implements keeps Harbor's name, table and meaning. A field ALE adds sits in the Harbor table of what it configures. schema_version "1.4+ale.1" marks the ALE file, and a Task reaches Harbor through a conversion. docs/specs/task-authoring.md:9-14 [doc]. The schema line is at taskspec.py:523-525 [code].
Deliberately unsupported Harbor features fail with named errors instead of unknown keys: steps, multi_step_reward_strategy, source, docker-compose sidecars, healthcheck, tpu, artifact destination/service, verifier collect and user. taskspec.py:550-557 [code], task-authoring.md:129-136 [doc].
ATIF trajectory. trajectory.json is a Harbor ATIF v1.8 document, not an ALE envelope. docs/specs/trace.md:23-26 [doc]. The checked fixture tests/fixtures/atif-v1.8.schema.json holds the Harbor pydantic schema with 12 defs (Agent, Observation, Step, ToolCall, Trajectory and friends, measured). Parity is verified by tests/conformance/test_harbor_atif.py. trace.md:274-276 [doc].
Exports. Harbor consumes trajectory.json directly, Prime Verifiers conversion and Prime-RL export live in packages/ale-run/src/ale/run/exporters.py with rules at trace.md:263-271 [doc].
ale-tasks-base. Named once, in docs/guides/development.md:92 as a Task repository that calls the public API. The @task-params format does not exist anywhere in this repo (no grep matches). [doc] [grep] [unknown].
Old engine agents-last-exam. No code or doc in this repo refers to an older engine. The old org name survives only as the HF asset namespace agents-last-exam. packages/ale-run/src/ale/run/assets.py:33 [code]. Everything else is Harbor-schema-compatible rewrite language. [inference].

## Open questions

1. What license applies to the engine repository? No LICENSE file and no license metadata exist. [unknown]
2. How does the 500-task conversion handle the old ale-tasks-base task-params style fields? Nothing in this engine consumes them. [unknown]
3. Where should machine, modality, subject, difficulty and cost metadata live for the conversion program? The engine has no field for any of them, so they must be a sidecar outside task.toml. [unknown]
4. Where is the Harbor to ALE conversion tool? task-authoring.md promises a conversion but no converter module ships in this snapshot. [unknown]
5. Is ale-tasks-base still the source of truth for task content, or has task authoring moved fully to the Harbor 1.4 task.toml format? Only one doc line references ale-tasks-base. [unknown]
6. How will the Windows tasks be converted and validated given the Windows base image is private and licensed? images/README.md:38-41. [unknown]
7. Does the team plan local Docker or QEMU validation, or Daytona cloud, for the 500-task run? All three are supported paths with different costs. [unknown]
8. Is macOS support needed for any of the 500 tasks? It requires Orchard and pinned Tart images plus open networking, the most restrictive path. [unknown]
9. What aggregation policy will score the 500 tasks? ALE deliberately ships no primary reward and leaves every reward map named and unaggregated. verdict.py:47-48. [unknown]
10. Will the conversion program adopt the two-decimal round-half-up reward rounding when comparing scores against the old engine? It changes borderline scores (0.995 to 1.0). verification.md:18-22. [unknown]
11. Are there official ALE datasets published on Hugging Face under agents-last-exam, and which naming do they use for task repos, agentslastexam or agents-last-exam? The two spellings coexist in this repo. [unknown]
12. Does the engine pin agent CLI versions that will change before the Linux validation runs? Every harness presets pin versions, and resume plus reportable results demand exact integrity, so pins matter for reproducible runs. [unknown]
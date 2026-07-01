# gm-cli Operations

This directory keeps gm-cli operational files out of the repository root.

Detailed workflow:

```text
../../doc/gm_cli_task_submission_workflow.md
```

Cloud artifact layout:

```text
../../doc/cloud_task_artifact_layout.md
```

## Payloads

Use this directory for request payloads:

```text
ops/gm-cli/payloads/
```

Committed templates:

```text
payloads/create-x1-dh-stand-smoke-template.json
payloads/create-x1-dh-stand-train-template.json
```

Local filled payloads should use a `.local.json` suffix and are ignored by Git:

```text
payloads/create-x1-dh-stand-smoke.local.json
payloads/create-x1-dh-stand-train.local.json
```

## Local Account Ledger

For multiple Gradmotion accounts, keep the local account ledger here:

```text
ops/gm-cli/accounts.local.json
```

This ledger is ignored by Git and must not contain API keys, passwords, GitHub tokens, signed URLs, or recharge records. Store only profile names, status, project/resource preferences, estimated quota fields, task usage records, and operational notes.

## Downloaded Task Artifacts

Keep downloaded cloud outputs outside `ops/`:

```text
cloud_artifacts/tasks/<TASK_ID>/
```

Expected per-task layout:

```text
metadata/task-info.json
metadata/model-list.json
logs/train.log
checkpoints/model_*.pt
tensorboard/
checksums.sha256
```

`cloud_artifacts/` is local-only and ignored by Git.

See `../../doc/cloud_task_artifact_layout.md` for file roles, metadata conventions, and checkpoint checksum policy.

## Inference Repository Sync

After a Gradmotion task completes, download and sync artifacts with:

```powershell
powershell -ExecutionPolicy Bypass -File .\ops\gm-cli\download-task-artifacts.ps1 -TaskId TASK_xxx
```

This copies the downloaded task directory to:

```text
F:\Projects\agibot_x1_infer\training\<TASK_ID>\
```

Writing to that destination may require an elevated shell.

For task directories that are already present under `cloud_artifacts/tasks/`, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\ops\gm-cli\sync-task-artifacts.ps1 -TaskId TASK_xxx
```

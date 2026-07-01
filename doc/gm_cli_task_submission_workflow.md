# gm-cli 云训练任务提交流程

本文档说明当前 X1 12DOF 项目如何使用 `gm-cli` 提交 Gradmotion 云训练任务、查看日志、下载产物。

## 1. 当前项目默认配置

| 项目 | 值 |
|---|---|
| Git 仓库 | `https://github.com/AgibotTech/agibot_x1_train.git` |
| 任务名 | `x1_dh_stand` |
| 训练入口 | `agibot_x1_train/humanoid/scripts/train.py` |
| 配置文件 | `agibot_x1_train/humanoid/envs/x1/x1_dh_stand_config.py` |
| smoke 模板 | `ops/gm-cli/payloads/create-x1-dh-stand-smoke-template.json` |
| train 模板 | `ops/gm-cli/payloads/create-x1-dh-stand-train-template.json` |

## 2. Windows 下调用 gm

PowerShell 里 `gm` 可能被解析成 `Get-Member` 别名。若遇到冲突，使用实际 gm-cli 可执行文件路径，或在当前 shell 中移除别名：

```powershell
Remove-Item Alias:gm -ErrorAction SilentlyContinue
gm --help
```

## 3. 准备 payload

复制模板：

```powershell
Copy-Item ops\gm-cli\payloads\create-x1-dh-stand-smoke-template.json `
  ops\gm-cli\payloads\create-x1-dh-stand-smoke.local.json
```

替换模板中的占位符：

```text
REPLACE_WITH_GRADMOTION_PROJECT_ID
REPLACE_WITH_RESOURCE_GOODS_ID
REPLACE_WITH_IMAGE_ID
REPLACE_WITH_IMAGE_VERSION
```

这些值需要通过你的 Gradmotion 账号查询：

```powershell
gm project list
gm resource list
gm image list
```

## 4. 创建和启动任务

创建任务：

```powershell
gm task create --json ops\gm-cli\payloads\create-x1-dh-stand-smoke.local.json
```

查看任务：

```powershell
gm task list
gm task info --task-id TASK_xxx
```

启动任务：

```powershell
gm task run --task-id TASK_xxx
```

查看日志：

```powershell
gm task logs --task-id TASK_xxx
```

停止任务：

```powershell
gm task stop --task-id TASK_xxx
```

## 5. 推荐 startScript

Smoke：

```bash
gm-run agibot_x1_train/humanoid/scripts/train.py --task=x1_dh_stand --headless --num_envs=16 --max_iterations=5
```

正式训练：

```bash
gm-run agibot_x1_train/humanoid/scripts/train.py --task=x1_dh_stand --headless --num_envs=4096 --max_iterations=3000 --run_name=x1_dh_stand_v1
```

## 6. 下载云端产物

下载任务信息、日志和模型列表：

```powershell
powershell -ExecutionPolicy Bypass -File .\ops\gm-cli\download-task-artifacts.ps1 -TaskId TASK_xxx
```

产物目录约定见：

```text
doc/cloud_task_artifact_layout.md
```

同步已下载任务产物：

```powershell
powershell -ExecutionPolicy Bypass -File .\ops\gm-cli\sync-task-artifacts.ps1 -TaskId TASK_xxx
```

## 7. Private 仓库注意

如果仓库是 private，需要确认 Gradmotion 的 Git 信息已经配置可读 token。验证标准：

```text
taskCodeInfo.commitId 不为空
日志中出现 /workspace/agibot_x1_train/
训练入口文件能被正常打开
```

若日志显示找不到：

```text
agibot_x1_train/humanoid/scripts/train.py
```

优先检查：

```text
codeUrl 仓库地址
mainCodeUri 路径前缀
Git token 权限
任务使用的 branch / commit
```

## 8. 不提交本地账号文件

以下内容只放本地，不提交：

```text
ops/gm-cli/accounts.local.json
ops/gm-cli/payloads/*.local.json
token
账号密码
```

# AGENTS.md

## 目的

本文件定义本仓库中代理长期遵守的工作规则、文档路由和安全边界。根目录 `AGENTS.md` 只保留全仓库通用且稳定的规则；详细训练、部署、对比和排障说明放入 `docs/`。

## 项目介绍

- 项目名称：`agi_train_29`
- 项目类型：Isaac Gym 人形机器人强化学习训练工程
- 核心任务：`x1_dh_stand`
- 机器人模型：X1 12DOF 腿部控制模型
- 主要目标：训练 X1 在仿真中完成站立、行走、转向和抗扰动，并支持 play、export、sim2sim、远端部署和 Gradmotion 云桌面训练。
- 主要技术栈：Python、PyTorch、Isaac Gym、PPO、MuJoCo sim2sim、Gradmotion/gm-cli 运维脚本。
- 默认训练入口：`humanoid/scripts/train.py --task=x1_dh_stand`
- 默认回放入口：`humanoid/scripts/play.py --task=x1_dh_stand`
- 核心配置：`humanoid/envs/x1/x1_dh_stand_config.py`

关键维度：

```text
num_actions = 12
num_single_obs = 47
num_observations = 3102
single_num_privileged_obs = 73
num_privileged_obs = 219
```

## 仓库工作规则

- `docs/assets/` 存放 README 使用的图片/GIF 等媒体素材；文字说明文档放入 `docs/`。
- 训练、部署、云桌面、gm-cli 和排障说明放在 `docs/ops/`。
- 项目对比和分析报告放在 `docs/reports/`。
- 运维脚本放在 `ops/`，其中 `ops/gradmotion/` 管理 Gradmotion GUI 云桌面和远端部署，`ops/gm-cli/` 管理云任务模板和产物下载。
- 不要提交私钥、token、账号密码、Gradmotion 临时链接、`ops/gm-cli/accounts.local.json`、`ops/gm-cli/payloads/*.local.json`、`cloud_artifacts/`、`outputs/` 或 `work/`。
- `ops/gradmotion/codex_gradmotion.pub` 是公钥，可以保留；对应私钥不能入库。
- 修改训练配置、动作维度、观测维度、关节顺序或默认关节角后，必须同步检查 play/export/sim2sim 和部署文档。
- 迁移 `E:\agi_29` 或 `E:\agi_origin` 的逻辑前，先阅读对应对比报告，确认 12DOF/29DOF 维度和奖励依赖是否兼容。

## 仓库地图

- `humanoid/`：训练环境、PPO 算法、脚本入口和任务注册。
- `resources/`：机器人 URDF/MJCF/mesh 等资源。
- `ops/gradmotion/`：Gradmotion GUI 云桌面、反向 SSH、远端部署、viewer smoke、训练和 TensorBoard 脚本。
- `ops/gm-cli/`：gm-cli 云任务模板、任务产物下载和同步脚本。
- `docs/`：项目说明、长期状态、Git 工作流、运维文档和分析报告。
- `docs/ops/`：远端部署、云桌面、gm-cli 和云任务产物说明。
- `docs/reports/`：当前项目与其他分支/项目的差异报告。
- `docs/assets/`：README 媒体素材。
- `work/`：本地缓存/临时资料，忽略不入库。

## 常用命令

安装当前项目：

```bash
python -m pip install -e .
```

训练：

```bash
python humanoid/scripts/train.py --task=x1_dh_stand --headless
```

小规模 smoke：

```bash
python humanoid/scripts/train.py --task=x1_dh_stand --headless --num_envs=16 --max_iterations=5
```

回放：

```bash
python humanoid/scripts/play.py --task=x1_dh_stand --load_run=<run_name>
```

Gradmotion GUI smoke：

```bash
NUM_ENVS=16 MAX_ITERATIONS=10 bash ops/gradmotion/gui-desktop-train.sh gui-smoke
```

远端部署打包：

```bash
bash ops/gradmotion/deploy_x1_remote.sh --package-only
```

脚本语法检查：

```bash
bash -n ops/gradmotion/bootstrap-gui-desktop.sh
bash -n ops/gradmotion/start-codex-tunnel.sh
bash -n ops/gradmotion/gui-desktop-train.sh
bash -n ops/gradmotion/deploy_x1_remote.sh
python -m json.tool ops/gm-cli/payloads/create-x1-dh-stand-smoke-template.json
python -m json.tool ops/gm-cli/payloads/create-x1-dh-stand-train-template.json
```

## 验证策略

- 修改 Python 训练逻辑后，优先运行小规模 `train.py --num_envs=16 --max_iterations=5` smoke；没有 Isaac Gym/GPU 环境时说明未运行原因。
- 修改 `ops/gradmotion/*.sh` 后，至少运行 `bash -n` 语法检查。
- 修改 gm-cli JSON 模板后，运行 `python -m json.tool <file>`。
- 修改 PowerShell 脚本后，用 PowerShell AST 解析检查语法。
- 修改部署或云桌面流程后，更新 `docs/ops/x1_remote_training_deployment.md` 或相关 `docs/ops/gradmotion*.md`。
- 修改长期项目状态、关键决策或下一步计划后，更新 `docs/project-state.md`。

## Git 协作职责

详细流程见 `docs/git-workflow.md`。

- 不要使用 `git add .`；只按路径暂存当前任务相关文件。
- 不要把无关改动带入当前提交。
- commit message 使用中文，除非用户要求其他格式。
- push、pull、merge、rebase、stash、reset、clean、force-push 和删除分支前必须得到用户确认。
- 默认禁止 `git reset --hard`、`git clean -fd`、破坏性 checkout 和 force-push。
- 发现本地提交未推送或远端权限异常时，主动说明当前分支、remote、提交哈希和下一步。

## 知识索引

| 主题 | 读取时机 | 来源 |
| --- | --- | --- |
| 项目整体运行思路 | 解释训练链路、奖励、PPO、观测或动作含义时 | `docs/CURRENT_PROJECT_OPERATION_GUIDE.md` |
| 当前 vs agi_29 | 比较或迁移 29DOF/F1 逻辑时 | `docs/reports/CURRENT_vs_AGI_29_DIFF_REPORT.md` |
| 当前 vs agi_origin | 比较 minimum-jerk、IK、实验奖励或 origin 分支时 | `docs/reports/CURRENT_vs_AGI_ORIGIN_DIFF_REPORT.md` |
| 远端部署 | 修改部署脚本、云桌面训练或远端环境时 | `docs/ops/x1_remote_training_deployment.md` |
| Gradmotion GUI 最小复现 | 连接新 GUI 云桌面或验证 Codex 可见 GUI 时 | `docs/ops/gradmotion_codex_gui_minimal_repro.md` |
| 反向 SSH GUI 工作流 | 排查云桌面 SSH 隧道、DISPLAY 或 XAUTHORITY 时 | `docs/ops/gradmotion_reverse_ssh_gui_workflow.md` |
| Codex GUI 操作原理 | 解释 Codex 如何操作 Gradmotion 桌面时 | `docs/ops/codex_gradmotion_gui_operation_principles.md` |
| gm-cli 云任务 | 创建、运行、下载或同步 Gradmotion 云任务时 | `docs/ops/gm_cli_task_submission_workflow.md` |
| 云任务产物布局 | 下载或整理云端 checkpoint、日志、metadata 时 | `docs/ops/cloud_task_artifact_layout.md` |
| Git 工作流 | commit、branch、push、merge、rebase、stash 或 PR 准备时 | `docs/git-workflow.md` |
| 项目状态 | 恢复上下文、规划下一步或记录阶段决策时 | `docs/project-state.md` |

## 层级化规则

- 全仓库长期规则写入根 `AGENTS.md`。
- 详细需求、测试方案、架构说明、部署步骤和排障手册写入 `docs/`。
- 可重复执行的运维流程优先写成 `ops/` 脚本。
- 某个子目录形成独立规则时，在对应目录新增局部 `AGENTS.md`。
- 如果知识索引中的文档不存在，不要臆造内容；按任务需要创建或说明缺失。

## 演进记录

- `2026-07-01`：将通用 AGENTS 模板适配为当前 X1 训练项目规则，统一文档路由、常用命令、验证策略和知识索引。


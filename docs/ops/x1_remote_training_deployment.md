# X1 12DOF 远端训练部署流程

本文档说明如何把当前 `agibot_x1_train` 项目部署到远端机器或 Gradmotion GUI 云桌面，并启动 `x1_dh_stand` 训练。

## 1. 项目信息

| 项目 | 值 |
|---|---|
| 默认任务 | `x1_dh_stand` |
| 机器人 | X1 12DOF 腿部控制模型 |
| 训练入口 | `humanoid/scripts/train.py` |
| 回放入口 | `humanoid/scripts/play.py` |
| 配置文件 | `humanoid/envs/x1/x1_dh_stand_config.py` |
| 日志目录 | `logs/x1_dh_stand/exported_data/` |

当前任务关键维度：

```text
num_actions = 12
num_single_obs = 47
num_observations = 3102
single_num_privileged_obs = 73
num_privileged_obs = 219
```

## 2. 一键部署脚本

脚本位置：

```bash
ops/gradmotion/deploy_x1_remote.sh
```

只打包当前项目：

```bash
bash ops/gradmotion/deploy_x1_remote.sh --package-only
```

上传并部署到远端：

```bash
bash ops/gradmotion/deploy_x1_remote.sh --server root@SERVER_IP --conda-env pointfoot_legged_gym --gpu 0
```

在远端本机从已有压缩包部署：

```bash
bash ops/gradmotion/deploy_x1_remote.sh \
  --local-deploy \
  --archive ./agibot_x1_train.tar.gz \
  --conda-env pointfoot_legged_gym \
  --gpu 0
```

跳过训练 smoke test，只做安装和配置检查：

```bash
bash ops/gradmotion/deploy_x1_remote.sh --server root@SERVER_IP --skip-smoke
```

## 3. Gradmotion GUI 云桌面

新云桌面已经 clone 本项目后，推荐先运行：

```bash
bash ops/gradmotion/bootstrap-gui-desktop.sh
```

这个脚本默认会：

```text
git pull
python -m pip install -e .
检查 GPU / DISPLAY / Isaac Gym / torch / x1_dh_stand 配置
运行 1-env GUI smoke
运行 16-env GUI smoke
```

如果只想跑 headless smoke：

```bash
bash ops/gradmotion/bootstrap-gui-desktop.sh --headless-smoke
```

正式训练：

```bash
RUN_NAME=x1_dh_stand_v1 bash ops/gradmotion/bootstrap-gui-desktop.sh --train
```

## 4. GUI 操作入口

脚本位置：

```bash
ops/gradmotion/gui-desktop-train.sh
```

常用命令：

```bash
bash ops/gradmotion/gui-desktop-train.sh install
bash ops/gradmotion/gui-desktop-train.sh check
bash ops/gradmotion/gui-desktop-train.sh gui-env
bash ops/gradmotion/gui-desktop-train.sh open-app xclock
bash ops/gradmotion/gui-desktop-train.sh gui-single
NUM_ENVS=16 MAX_ITERATIONS=10 bash ops/gradmotion/gui-desktop-train.sh gui-smoke
NUM_ENVS=64 MAX_ITERATIONS=20 bash ops/gradmotion/gui-desktop-train.sh headless-smoke
NUM_ENVS=4096 MAX_ITERATIONS=3000 RUN_NAME=x1_dh_stand_v1 bash ops/gradmotion/gui-desktop-train.sh train
LOAD_RUN=x1_dh_stand_v1 bash ops/gradmotion/gui-desktop-train.sh play
bash ops/gradmotion/gui-desktop-train.sh tensorboard
```

说明：`gui-hold-focused` 会优先尝试 `humanoid/scripts/train_focused_view.py`。如果当前项目没有这个脚本，请使用普通 `gui-hold` 或 `gui-smoke`。

## 5. Codex 远程操作云桌面

新 Gradmotion GUI 云桌面可以使用：

```bash
bash ops/gradmotion/start-codex-tunnel.sh
```

如果 ECS 需要指定 SSH 私钥，从云桌面运行：

```bash
bash ops/gradmotion/start-codex-tunnel.sh --identity-file /root/.ssh/codex_tunnel_to_ecs
```

它会做三件事：

```text
把 Codex 公钥加入云桌面 /root/.ssh/authorized_keys
运行 GUI bootstrap
通过 ECS 跳板机建立反向 SSH 隧道
```

隧道建立后，Codex 可以通过 ECS 反向端口进入云桌面执行命令；用户仍然能在 Gradmotion GUI 桌面看到 Isaac Gym viewer、xclock、终端等窗口。

详细原理见：

```text
docs/ops/codex_gradmotion_gui_operation_principles.md
docs/ops/gradmotion_reverse_ssh_gui_workflow.md
docs/ops/gradmotion_codex_gui_minimal_repro.md
```

## 6. TensorBoard

云桌面或远端机器上启动：

```bash
bash ops/gradmotion/gui-desktop-train.sh tensorboard
```

等价命令：

```bash
tensorboard --logdir logs/x1_dh_stand --host 0.0.0.0 --port 6006
```

如果需要本地访问：

```bash
ssh -L 6006:localhost:6006 root@SERVER_IP
```

然后打开：

```text
http://localhost:6006
```

## 7. gm-cli 云任务模板

模板在：

```text
ops/gm-cli/payloads/create-x1-dh-stand-smoke-template.json
ops/gm-cli/payloads/create-x1-dh-stand-train-template.json
```

提交前需要替换：

```text
REPLACE_WITH_GRADMOTION_PROJECT_ID
REPLACE_WITH_RESOURCE_GOODS_ID
REPLACE_WITH_IMAGE_ID
REPLACE_WITH_IMAGE_VERSION
```

这些值依赖你的 Gradmotion 账号、项目、镜像和资源规格。

## 8. 安全注意

不要把以下内容提交到仓库：

```text
私钥
token
账号密码
Gradmotion 临时登录链接
ops/gm-cli/accounts.local.json
cloud_artifacts/
outputs/
```

`ops/gradmotion/codex_gradmotion.pub` 是公钥，可以保留在仓库里；对应私钥必须只留在本地。


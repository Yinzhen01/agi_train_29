# Gradmotion GUI 云桌面最小复现流程

本文档用于在新的 Gradmotion GUI 云桌面上快速验证：Codex 可以远程进入云桌面、打开可见 GUI 程序，并运行当前项目的 `x1_dh_stand` viewer smoke test。

## 1. 云桌面侧启动隧道

在 Gradmotion GUI 云桌面里打开终端，进入项目目录：

```bash
cd /root/limx_rl/agi_train_29
```

启动一键入口：

```bash
bash ops/gradmotion/start-codex-tunnel.sh
```

如果环境已经安装好，只想重建隧道：

```bash
bash ops/gradmotion/start-codex-tunnel.sh --no-bootstrap
```

多台云桌面同时连接时，为每台分配不同端口：

```bash
bash ops/gradmotion/start-codex-tunnel.sh --remote-port 2222
bash ops/gradmotion/start-codex-tunnel.sh --remote-port 2223
```

## 2. Codex 侧验证 SSH

隧道建立后，从本地通过 ECS 反向端口进入云桌面：

```bash
ssh -i ~/.ssh/codex_gradmotion_ed25519 -p 2222 root@<ECS_PUBLIC_IP> \
  "hostname && pwd && echo tunnel-login-ok"
```

看到云桌面 hostname 和 `tunnel-login-ok` 即表示 SSH 链路可用。

## 3. 验证 GUI 显示

在 SSH 进入的云桌面 shell 中运行：

```bash
cd /root/limx_rl/agi_train_29
bash ops/gradmotion/gui-desktop-train.sh gui-env
bash ops/gradmotion/gui-desktop-train.sh open-app xclock
```

如果用户正在看的 Gradmotion 桌面出现 `xclock` 窗口，说明 `DISPLAY/XAUTHORITY` 识别正确，Codex 启动的 GUI 会显示在用户可见桌面里。

## 4. 运行 X1 GUI smoke

最小 viewer：

```bash
cd /root/limx_rl/agi_train_29
bash ops/gradmotion/gui-desktop-train.sh gui-single
```

16 环境 viewer smoke：

```bash
NUM_ENVS=16 MAX_ITERATIONS=10 bash ops/gradmotion/gui-desktop-train.sh gui-smoke
```

小规模 headless smoke：

```bash
NUM_ENVS=64 MAX_ITERATIONS=20 bash ops/gradmotion/gui-desktop-train.sh headless-smoke
```

## 5. 后台保持 Viewer

启动一个后台 viewer：

```bash
RUN_NAME=x1_gui_hold_YYYYMMDD bash ops/gradmotion/gui-desktop-train.sh gui-hold
```

查看状态：

```bash
RUN_NAME=x1_gui_hold_YYYYMMDD bash ops/gradmotion/gui-desktop-train.sh gui-hold-status
```

停止：

```bash
RUN_NAME=x1_gui_hold_YYYYMMDD bash ops/gradmotion/gui-desktop-train.sh stop-gui-hold
```

说明：`gui-hold-focused` 需要当前项目存在 `humanoid/scripts/train_focused_view.py`。没有这个脚本时使用 `gui-hold`。

## 6. 正式训练和回放

正式训练：

```bash
NUM_ENVS=4096 MAX_ITERATIONS=3000 RUN_NAME=x1_dh_stand_v1 \
  bash ops/gradmotion/gui-desktop-train.sh train
```

回放：

```bash
LOAD_RUN=x1_dh_stand_v1 bash ops/gradmotion/gui-desktop-train.sh play
```

TensorBoard：

```bash
bash ops/gradmotion/gui-desktop-train.sh tensorboard
```

日志目录：

```text
logs/x1_dh_stand/exported_data/<timestamp><RUN_NAME>/
```

## 7. 清理

不再需要 Codex 操作该云桌面时：

```text
关闭保持 start-codex-tunnel.sh 的终端
必要时从 /root/.ssh/authorized_keys 删除临时公钥
```

不要把私钥、token、临时登录链接写入仓库或聊天记录。

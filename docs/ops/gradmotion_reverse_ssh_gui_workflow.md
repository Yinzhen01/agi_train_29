# Gradmotion 反向 SSH GUI 工作流

本文档说明 Codex 如何通过反向 SSH 操作 Gradmotion GUI 云桌面，并让 Isaac Gym viewer 等窗口显示在用户正在看的云桌面里。

## 1. 架构

Gradmotion GUI 云桌面通常不能直接从公网 SSH 进入，所以使用 ECS 跳板机：

```text
Gradmotion 云桌面
  -> 主动连接 ECS
  -> ssh -N -R <REMOTE_PORT>:localhost:22 root@<ECS_PUBLIC_IP>

Codex / 本地机器
  -> ssh -p <REMOTE_PORT> root@<ECS_PUBLIC_IP>
  -> 实际进入 Gradmotion 云桌面的 localhost:22
```

核心是：云桌面主动连出，建立反向端口映射。只要这个隧道不断开，Codex 就可以通过 ECS 端口管理云桌面。

## 2. 云桌面一键入口

在 Gradmotion GUI 云桌面终端中：

```bash
cd /root/limx_rl/agibot_x1_train
bash ops/gradmotion/start-codex-tunnel.sh
```

如果项目和环境已经准备好，只恢复隧道：

```bash
bash ops/gradmotion/start-codex-tunnel.sh --no-bootstrap
```

多台云桌面并行：

```bash
bash ops/gradmotion/start-codex-tunnel.sh --remote-port 2222
bash ops/gradmotion/start-codex-tunnel.sh --remote-port 2223
bash ops/gradmotion/start-codex-tunnel.sh --remote-port 2224
```

## 3. 本地/Codex 登录

```bash
ssh -i ~/.ssh/codex_gradmotion_ed25519 -p 2222 root@<ECS_PUBLIC_IP> \
  "hostname && pwd && echo tunnel-login-ok"
```

如果输出云桌面 hostname，说明反向 SSH 可用。

## 4. GUI 显示原理

Codex 通过 SSH 登录后默认是 root shell，不一定天然在用户正在看的图形会话中。要让窗口显示到云桌面，需要正确设置：

```text
DISPLAY
XAUTHORITY
XDG_RUNTIME_DIR
```

项目脚本会自动探测这些变量：

```bash
bash ops/gradmotion/gui-desktop-train.sh gui-env
bash ops/gradmotion/gui-desktop-train.sh open-app xclock
```

`xclock` 能显示在云桌面上，就说明 GUI 链路打通。

## 5. X1 Viewer / 训练命令

最小 viewer：

```bash
bash ops/gradmotion/gui-desktop-train.sh gui-single
```

16 环境 viewer smoke：

```bash
NUM_ENVS=16 MAX_ITERATIONS=10 bash ops/gradmotion/gui-desktop-train.sh gui-smoke
```

后台 viewer：

```bash
RUN_NAME=x1_gui_hold_YYYYMMDD bash ops/gradmotion/gui-desktop-train.sh gui-hold
```

状态和停止：

```bash
RUN_NAME=x1_gui_hold_YYYYMMDD bash ops/gradmotion/gui-desktop-train.sh gui-hold-status
RUN_NAME=x1_gui_hold_YYYYMMDD bash ops/gradmotion/gui-desktop-train.sh stop-gui-hold
```

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

## 6. 常见问题

没有窗口显示：

```bash
bash ops/gradmotion/gui-desktop-train.sh gui-env
bash ops/gradmotion/gui-desktop-train.sh open-app xclock
```

如果 `xclock` 都不显示，优先检查 `DISPLAY/XAUTHORITY` 和云桌面是否有活跃图形会话。

隧道断开：

```bash
ssh -p 2222 root@<ECS_PUBLIC_IP> "hostname"
```

无法连接时，回到云桌面终端重新运行：

```bash
bash ops/gradmotion/start-codex-tunnel.sh --no-bootstrap --remote-port 2222
```

训练还在但 SSH 命令超时：

```bash
ps aux | grep humanoid/scripts/train.py
nvidia-smi
tail -n 100 /tmp/codex_isaac_viewer_hold.log
```

## 7. 安全边界

不要提交或公开：

```text
ECS 密码
SSH 私钥
Gradmotion token
云桌面临时登录链接
```

不再需要 Codex 操作云桌面时，关闭保持 `start-codex-tunnel.sh` 的终端；如果使用的是临时公钥，也应从 `/root/.ssh/authorized_keys` 删除。

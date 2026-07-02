# 当前项目 vs E:\agi_origin 差异分析报告

生成时间：2026-06-30  
当前项目：`E:\agi_train_29`
对比项目：`E:\agi_origin`  
对比范围：排除 `.git` 内部对象；旧报告、实验目录、代码、资源均记录，但分析重点放在业务差异。  

## 1. 总体结论

`E:\agi_origin` 与当前项目同属 12DOF X1 路线，核心 PPO、utils、base 环境和大部分资源文件保持一致。它不是 29DOF 扩展版，而是一个带实验记录、诊断脚本、训练指标包装器、IK 摆腿参考和 CSV 采集逻辑的实验版。

当前项目更干净、更接近基础训练版：保留原始正弦摆腿参考，训练迭代数为 20000，保存间隔 100，并带有 `docs/assets/` 演示资源。`agi_origin` 则更偏 6.x 实验过程：将 URDF 文件改为 `X1_12DOF.urdf`，引入 minimum-jerk 足端轨迹和近似 IK，增加髋 yaw/roll 与左右腿对称奖励，把训练迭代数改成 50，并额外提供 GradMotion metrics 解析脚本和大量诊断 CSV/实验记录。

## 2. 版本与文件规模

| 项目 | 最近提交 | 文件数 | 总大小 | 主要差异 |
|---|---:|---:|---:|---|
| 当前项目 | `e6651b9 first commit` | 104 | 303.05 MB | 含 `docs/assets/` 图片/GIF；基础 12DOF 训练版 |
| `E:\agi_origin` | `5a839c4 添加训练测试代码` | 111 | 70.58 MB | 含 `czy` 实验目录、旧报告、诊断脚本 |

文件哈希对比结果：

| 类别 | 数量 |
|---|---:|
| 同路径共同文件 | 95 |
| 同路径且内容一致 | 91 |
| 同路径但内容不同 | 4 |
| 仅当前项目存在 | 9 |
| 仅 `agi_origin` 存在 | 16 |

同路径但内容不同的文件：

- `setup.py`
- `humanoid/envs/x1/x1_dh_stand_config.py`
- `humanoid/envs/x1/x1_dh_stand_env.py`
- `humanoid/scripts/play.py`

说明：`agi_origin` 的绝大多数框架代码与当前项目一致，差异高度集中在 X1 站立/行走任务和实验辅助链路。

## 3. 项目结构差异

当前项目独有：

- `docs/assets/id.jpg`
- `docs/assets/joy_map.jpg`
- `docs/assets/mujoco.gif`
- `docs/assets/play.gif`
- `docs/assets/train.gif`
- `resources/robots/x1/urdf/x1.urdf`
- `resources/robots/x1/meshes/lumber_pitch.STL`
- `resources/robots/x1/meshes/lumber_roll.STL`
- `resources/robots/x1/meshes/lumber_yaw.STL`

`agi_origin` 独有：

- `AGI_29_COMPARISON_REPORT.md`
- `CURRENT_PROJECT_DIFF_REPORT.md`
- `humanoid/scripts/train_with_metrics.py`
- `resources/robots/x1/urdf/X1_12DOF.urdf`
- `resources/robots/x1/meshes/lumbar_pitch_x1.STL`
- `resources/robots/x1/meshes/lumbar_roll.STL`
- `resources/robots/x1/meshes/lumbar_yaw.STL`
- `czy/data/*.csv`
- `czy/exp1/*.py`
- `czy/exp1/实验记录/exp1.md`

`czy` 目录明显是实验分析产物，包含 Isaac 诊断 CSV、多个分析脚本和实验记录，不属于当前项目的核心训练框架。

## 4. 资源与机器人模型差异

### 4.1 URDF 差异

| 指标 | 当前项目 `x1.urdf` | `agi_origin` `X1_12DOF.urdf` |
|---|---:|---:|
| links | 58 | 60 |
| joints | 57 | 59 |
| fixed joints | 45 | 47 |
| revolute joints | 12 | 12 |
| 可动关节顺序 | 双腿 12 关节 | 双腿 12 关节 |

两者都是 12DOF 可动腿部模型，可训练动作维度一致。但 `X1_12DOF.urdf` 保留更多固定 link，link 命名更偏 `*_link`，并将若干 `lumber_*` 拼写修正为 `lumbar_*`。

### 4.2 MJCF 差异

| 指标 | 当前项目 | `agi_origin` |
|---|---:|---:|
| MJCF robot 文件 | `xyber_x1_serial.xml` | `xyber_x1_serial.xml` |
| bodies | 30 | 30 |
| hinge joints | 12 | 12 |
| actuators | 12 | 12 |

MJCF robot 文件内容一致，说明 MuJoCo sim2sim 所用模型没有变化。差异主要发生在 Isaac Gym 加载的 URDF。

### 4.3 STL 网格

当前项目与 `agi_origin` 的 mesh 做命名映射后，65 个网格内容全部一致：

- 当前 `lumber_roll.STL` 对应 `agi_origin/lumbar_roll.STL`
- 当前 `lumber_yaw.STL` 对应 `agi_origin/lumbar_yaw.STL`
- 当前 `lumber_pitch.STL` 对应 `agi_origin/lumbar_pitch_x1.STL`

也就是说，mesh 几何基本没有变化，主要是文件名拼写和 URDF 引用变了。

## 5. 训练配置差异

核心配置文件：`humanoid/envs/x1/x1_dh_stand_config.py`

### 5.1 基础维度保持一致

| 配置项 | 当前项目 | `agi_origin` |
|---|---:|---:|
| `num_actions` | 12 | 12 |
| `num_single_obs` | 47 | 47 |
| `frame_stack` | 66 | 66 |
| `num_observations` | 3102 | 3102 |
| `single_num_privileged_obs` | 73 | 73 |
| `c_frame_stack` | 3 | 3 |
| `num_privileged_obs` | 219 | 219 |
| `default_joint_angles` | 12 项 | 12 项 |

这意味着当前项目与 `agi_origin` 的策略网络输入/输出维度兼容，至少不会因为 action 或 observation 维度不同而无法加载。

### 5.2 asset 配置差异

| 配置项 | 当前项目 | `agi_origin` |
|---|---|---|
| `asset.file` | `resources/robots/x1/urdf/x1.urdf` | `resources/robots/x1/urdf/X1_12DOF.urdf` |
| `asset.xml_file` | `resources/robots/x1/mjcf/xyber_x1_flat.xml` | 同当前项目 |

这会影响 Isaac Gym 训练时加载的刚体结构、质量、惯量、fixed link 命名等；但 sim2sim 的 MJCF 路径没有变。

### 5.3 奖励参数差异

`agi_origin` 移除了当前项目的固定 `final_swing_joint_delta_pos` 列表，改为一组 foot trajectory + IK 参数：

- `default_foot_pos`
- `foot_separation_y`
- `swing_height = 0.15`
- `step_length = 0.12`
- `ankle_roll_amplitude = 0.05`
- `ik_thigh_length = 0.2678`
- `ik_shank_length = 0.3068`
- `ik_ankle_height = 0.041`
- `ik_hip_pitch_offset = 0.0`
- `ik_knee_offset = 0.49`
- `ik_ankle_pitch_offset = -0.21`

### 5.3.1 foot trajectory + IK 参数解释

这些参数可以分成两组：前一组描述“脚应该怎么走”，后一组描述“怎么把脚的位置近似换算成腿关节角”。

| 参数 | 含义 | 在代码中的作用 | 调大/调小影响 |
|---|---|---|---|
| `default_foot_pos = [[0.0, 0.10, -0.041], [0.0, -0.10, -0.041]]` | 左右脚相对身体的默认足端位置。每个脚是 `[x, y, z]`。左脚 y 为 `0.10`，右脚 y 为 `-0.10`，表示左右脚默认横向间距；z 为 `-0.041`，表示脚端在踝关节下方约 4.1 cm。 | `compute_ref_state()` 用它作为左右脚轨迹的起点；`_solve_2d_leg_ik()` 用它计算足端偏移 `dx = x - default_x`、`dz = z - default_z`。 | x 改变会影响默认前后落脚位置；y 改变会影响站宽；z 改变会影响脚相对踝关节/身体的默认高度。这个值不准会导致 IK 参考角整体偏。 |
| `foot_separation_y = 0.20` | 左右脚默认横向距离，理论上等于 `0.10 - (-0.10) = 0.20`。 | 在当前 `agi_origin` 代码中没有直接参与计算，更多是配置说明或预留参数；实际横向距离由 `default_foot_pos` 的 y 值决定。 | 若未来代码用它生成 `default_foot_pos`，调大会让站姿更宽，调小会让双脚更近。当前版本直接改它基本不会生效。 |
| `swing_height = 0.15` | 摆动脚最高抬脚高度，相对默认 z 位置增加 0.15 m。 | `left_mid_z = left_start[:, 2] + self.swing_height`，右脚同理。z 方向轨迹用两段 minimum-jerk：默认高度到最高点，再从最高点回到默认高度。 | 调大：抬脚更高，更不容易拖地，但能耗和落地冲击可能变大。调小：步态更贴地、更省力，但容易绊脚或脚尖擦地。 |
| `step_length = 0.12` | 标称步长，表示摆动脚在 x 方向向前移动的最大距离。 | 实际步长会随命令速度缩放：`step_length = self.step_length * clamp(abs(cmd_vel) / 0.4, 0.3, 1.0)`。速度很小时仍保留 30% 步长，速度到 0.4 m/s 及以上时使用完整 0.12 m。 | 调大：步幅更大，理论速度潜力更高，但稳定性更难。调小：更稳、更保守，但可能走不快。 |
| `ankle_roll_amplitude = 0.05` | 支撑相中的踝部滚动幅度，注释里说从原 `0.12` 降到 `0.05`，用于减少足跟-足尖滚动幅度。 | 当前代码实际把它加到了 `ankle_pitch_delta`：`stance_roll = amplitude * sin(pi * stance_phase)`，再叠加到踝 pitch 目标。名字叫 roll，但实现里作用在 ankle pitch 上，更像支撑相脚掌滚动/踝 pitch 补偿。 | 调大：支撑脚滚动更明显，可能帮助推进，但容易引入踝部抖动或落地不稳。调小：脚掌更平稳，但推进感和自然滚动会减弱。 |
| `ik_thigh_length = 0.2678` | 大腿等效长度，近似 hip_pitch 到 knee_pitch 的距离。 | 在 `_solve_2d_leg_ik()` 中作为 `L1`，参与 `hip_pitch_delta = dx / (L1 + L2) * 1.2`。 | 调大：同样的前后足端偏移会换算成更小的髋 pitch 变化。调小：同样偏移会导致更大的髋 pitch 变化。 |
| `ik_shank_length = 0.3068` | 小腿等效长度，近似 knee_pitch 到 ankle_pitch 的距离。 | 在 `_solve_2d_leg_ik()` 中作为 `L2`，参与 `knee_delta = dz / L2 * 0.8`，也参与髋 pitch 分母 `L1 + L2`。 | 调大：同样抬脚高度换算成更小的膝盖变化。调小：膝盖会更明显弯曲，可能抬脚更激进。 |
| `ik_ankle_height = 0.041` | 踝关节到足端/脚底的高度偏移，约 4.1 cm。 | 当前代码里没有直接读取 `self.ik_ankle_height`，但同样的数值体现在 `default_foot_pos` 的 z 值 `-0.041` 和奖励参数 `feet_to_ankle_distance = 0.041` 中。 | 这个值本应影响足端高度和接触几何。当前版本直接改它基本不会生效，除非同步改 `default_foot_pos` 或代码逻辑。 |
| `ik_hip_pitch_offset = 0.0` | IK 结果到实际 hip pitch 关节角之间的补偿偏置。 | 当前代码读取到了 `self.ik_hip_pitch_offset`，但 `_solve_2d_leg_ik()` 没有实际使用它。真实 hip pitch 目标使用 `default_hip_pitch + hip_pitch_delta`。 | 当前版本直接改它不会影响轨迹。若未来接入，可用于修正 IK 解和 URDF 默认角之间的系统偏差。 |
| `ik_knee_offset = 0.49` | IK 结果到实际 knee pitch 关节角之间的补偿偏置，数值接近默认膝盖角。 | 当前代码读取到了 `self.ik_knee_offset`，但没有直接使用；膝盖目标来自 `default_knee + knee_delta`，其中 `default_knee` 已经包含默认角。 | 当前版本直接改它不会影响轨迹。概念上它表示膝关节默认弯曲补偿。 |
| `ik_ankle_pitch_offset = -0.21` | IK 结果到实际 ankle pitch 关节角之间的补偿偏置，数值接近默认踝 pitch。 | 当前代码读取到了 `self.ik_ankle_pitch_offset`，但没有直接使用；踝目标来自 `default_ankle_pitch - hip_pitch_delta * 0.5 - knee_delta * 0.3 + ankle_pitch_delta`。 | 当前版本直接改它不会影响轨迹。概念上它用于把几何 IK 的踝角映射到实际机器人关节零位。 |

用更通俗的话说：

```text
default_foot_pos       决定脚从哪里开始
step_length            决定脚往前迈多远
swing_height           决定脚抬多高
ankle_roll_amplitude   决定支撑脚滚动/踝部补偿有多明显
ik_thigh_length        告诉 IK 大腿有多长
ik_shank_length        告诉 IK 小腿有多长
ik_*_offset            理论上用于修正 IK 角度和真实关节零位的偏差
```

需要特别注意的是，当前 `agi_origin` 这版 IK 不是完整解析 IK，而是一个简化 Jacobian 映射：

```text
足端向前 dx  -> 主要换算成 hip_pitch_delta
足端抬高 dz  -> 主要换算成 knee_delta
hip/knee 变化 -> 再反向补偿 ankle_pitch
```

所以这些参数并不是越精确越一定好，还要看训练奖励、URDF 动力学和实际策略能否学到稳定动作。尤其是 `foot_separation_y`、`ik_ankle_height` 和三个 `ik_*_offset`，在当前代码中不是核心生效参数，调参优先级低于 `step_length`、`swing_height`、`ankle_roll_amplitude`、`ik_thigh_length`、`ik_shank_length`。

奖励权重变化：

| 奖励项 | 当前项目 | `agi_origin` | 影响 |
|---|---:|---:|---|
| `ref_joint_pos` | 2.2 | 1.0 | 降低对参考关节角的硬跟随 |
| `hip_yaw_roll_default` | 无 | 2.5 | 新增，约束髋 yaw/roll 接近默认 |
| `leg_symmetry` | 无 | 1.5 | 新增，约束左右腿运动幅度对称 |
| `feet_clearance` | 1.0 | 1.8 | 更鼓励抬脚 |
| `feet_air_time` | 1.2 | 1.8 | 更鼓励摆动相 |
| `default_joint_pos` | 1.0 | 0.3 | 降低默认姿态约束 |
| `orientation` | 1.0 | 1.2 | 略增强躯干姿态 |

其余主干奖励，如速度跟踪、接触力、能量、碰撞、站立等大体保持一致。

### 5.4 PPO 训练参数差异

| 配置项 | 当前项目 | `agi_origin` | 影响 |
|---|---:|---:|---|
| `max_iterations` | 20000 | 50 | `agi_origin` 明显是短测试配置 |
| `save_interval` | 100 | 5 | 更频繁保存，适合调试 |
| `learning_rate` | `1e-5` | `1e-5` | 相同 |
| `entropy_coef` | 0.001 | 0.001 | 相同 |
| `resume` | `False` | `False` | 相同 |

如果直接用 `agi_origin` 配置训练，会很快结束，不能与当前项目的长期训练设置等价比较。

## 6. 环境实现差异

核心文件：`humanoid/envs/x1/x1_dh_stand_env.py`

当前项目的 `compute_ref_state()` 使用简单正弦相位生成腿部 12 关节参考：

- 左腿在半周期内摆动
- 右腿在另半周期内摆动
- `ref_action = 2 * ref_dof_pos`
- 最后加上 `default_dof_pos`

### 6.1 `final_swing_joint_delta_pos` 如何按时间指导训练

当前项目中的 `final_swing_joint_delta_pos` 本身不是时间序列，而是一组“摆动腿最大关节偏移模板”。真正提供时间变化的是步态相位 `phase` 以及由它计算出的 `sin_pos`。

可以把两者理解为：

```text
final_swing_joint_delta_pos = 摆腿动作的形状模板
phase / sin_pos = 当前走到了这个动作的第几帧
```

每个仿真步都会根据当前相位生成一次新的参考关节角：

```text
当前参考关节角 = 默认关节角 + 相位系数 * final_swing_joint_delta_pos
```

例如左膝的最大偏移是 `0.35 rad`，但训练时不是每一帧都加满 `0.35`，而是随相位逐渐变化：

```text
摆腿刚开始：相位系数 0.0，偏移 0
摆腿中间：相位系数 0.5，偏移 0.175
摆腿峰值：相位系数 1.0，偏移 0.35
摆腿结束：相位系数回到 0，偏移 0
```

代码逻辑上，左腿使用正弦波的一半周期，右腿使用另一半周期：

```text
左腿参考偏移 = -sin_pos_l * final_swing_joint_delta_pos[左腿]
右腿参考偏移 =  sin_pos_r * final_swing_joint_delta_pos[右腿]
```

然后 `_reward_ref_joint_pos()` 在每个时间步比较真实关节角 `dof_pos` 和当前参考角 `ref_dof_pos`。越接近当前参考姿态，奖励越高；偏离越大，奖励越低。

因此这套奖励不是“静态地要求机器人永远保持一个姿势”，而是：

```text
静态关节模板 + 动态步态相位 = 每个时间步的参考轨迹
```

通俗地说，`final_swing_joint_delta_pos` 像一张关键姿势图，`phase/sin_pos` 像动画进度条。每一帧程序都会根据进度条把关键姿势缩放成当前帧目标姿势，再用奖励告诉策略这一帧像不像目标动作。

`agi_origin` 重写为 foot trajectory + IK 路线：

1. 新增 `_min_jerk()`，用 minimum-jerk 插值生成平滑足端轨迹。
2. 新增 `_solve_2d_leg_ik()`，根据足端 x/z 偏移近似映射到 hip/knee/ankle pitch。
3. `compute_ref_state()` 先构造左右脚目标位置，再求左右腿 6DOF 参考角。
4. 步长随命令速度缩放，但限制在一定范围内。
5. 新增支撑相 ankle roll 逻辑，模拟足跟到足尖滚动。
6. `ref_action = (ref_dof_pos - default_dof_pos) / action_scale`，与当前项目的 `2 * ref_dof_pos` 不同。

新增奖励函数：

- `_reward_hip_yaw_roll_default`
- `_reward_leg_symmetry`

奖励函数数量：

| 项目 | reward 函数数 |
|---|---:|
| 当前项目 | 30 |
| `agi_origin` | 32 |

这些改动说明 `agi_origin` 的实验重点是解决 12DOF 走路中的足端轨迹、髋 yaw/roll 偏移、左右腿不对称和抬脚不足问题。

### 6.2 minimum-jerk 足端轨迹来源

minimum-jerk 足端轨迹来自经典轨迹优化问题：在给定起点、终点、起止速度和起止加速度的情况下，让整段运动的 jerk 最小。jerk 是加速度的变化率：

```text
位置 p(t)
速度 v(t) = dp/dt
加速度 a(t) = d2p/dt2
jerk j(t) = d3p/dt3
```

优化目标通常写成：

```text
min ∫0^T || d3p(t) / dt3 ||^2 dt
```

常用边界条件是：

```text
p(0) = p0, p(T) = pf
v(0) = 0,  v(T) = 0
a(0) = 0,  a(T) = 0
```

也就是脚从起点平滑离开，到终点平滑落下，起点和终点处速度、加速度都为 0。令归一化相位 `s = t / T`，满足这些条件的五次插值函数为：

```text
f(s) = 10s^3 - 15s^4 + 6s^5
p(s) = p0 + (pf - p0) * f(s)
```

这个五次多项式可以从：

```text
f(s) = a0 + a1s + a2s^2 + a3s^3 + a4s^4 + a5s^5
```

配合 `f(0)=0`、`f(1)=1`、`f'(0)=0`、`f'(1)=0`、`f''(0)=0`、`f''(1)=0` 解出。它的意义是让足端起步和落地都没有突变，比直接线性插值或粗糙正弦关节参考更适合控制接触冲击。

在 `agi_origin` 的 `compute_ref_state()` 中，它的使用方式可以概括为：

1. 根据步态相位判断左腿或右腿处于摆动相。
2. 在 x 方向，用 minimum-jerk 把足端从起始落脚点平滑移动到下一落脚点。
3. 在 z 方向，分两段 minimum-jerk：地面高度到抬脚高度，再从抬脚高度回到地面高度。
4. y 方向主要维持默认左右脚间距。
5. 生成足端目标后，再通过 `_solve_2d_leg_ik()` 近似映射为髋、膝、踝关节角参考。

因此，`agi_origin` 的路线是“先规划脚怎么走，再反算腿关节怎么动”；当前项目则是“直接用正弦相位生成关节角参考”。前者运动学直觉更强，但依赖足端几何、IK 参数和 URDF 尺寸是否准确。

## 7. 播放与诊断脚本差异

### 7.1 `play.py`

`agi_origin` 的 `play.py` 比当前项目多了大量诊断能力：

- 默认 `RENDER = True`
- 默认 `LOG_CSV = True`
- 默认 `FIX_COMMAND = True`
- 固定命令速度 `PLAY_CMD_VEL_X = 0.4`
- 视频保存到 `/personal/train-more`
- 相机位置从 `(1, -1, 0.5)` 改为 `(2.0, -2.0, 1.5)`
- 在正式评估前 warmup `frame_stack` 步，填充 obs history
- CSV 记录动作、关节位置/速度/力矩、期望位置、接触力、IMU、base velocity 等
- 使用 `env.feet_indices` 而不是硬编码 body index 读取左右脚
- 视频叠加命令速度、实际速度、平均速度、左右脚接触状态、双支撑/腾空状态

当前项目的 `play.py` 更适合普通播放；`agi_origin` 的 `play.py` 更适合问题诊断和数据采集。

### 7.2 `train_with_metrics.py`

`agi_origin` 独有 `humanoid/scripts/train_with_metrics.py`。它包装 `train.py`，读取 stdout 中的：

- `Learning iteration`
- `Mean reward`
- `Value function loss`
- `Surrogate loss`

然后写入 `GRADMOTION_METRICS_FILE` 指定的 JSONL 文件。它还带有 `--self-test` 逻辑，用于验证日志解析。

这说明 `agi_origin` 曾经接入过 GradMotion 或类似平台的指标上报链路。当前项目没有这部分能力。

### 7.3 `setup.py`

`agi_origin` 多了依赖：

- `pygame`

当前项目未声明。若使用 joystick 或相关交互功能，当前项目可能需要补上。

## 8. 实验目录差异

`agi_origin` 独有 `czy` 目录，包含：

- `czy/data/isaac_diag_20260624_122059.csv`
- `czy/data/isaac_diag_20260624_155216.csv`
- `czy/data/isaac_diag_20260624_183924.csv`
- `czy/exp1/analyze_6_4.py`
- `czy/exp1/analyze_6_5.py`
- `czy/exp1/analyze_6_6.py`
- `czy/exp1/analyze_6_7.py`
- `czy/exp1/verify_ik_geometric.py`
- `czy/exp1/实验记录/exp1.md`

从文件名和代码结构看，这些是围绕 6.4 到 6.8 版本实验的诊断数据、分析脚本和 IK 验证工具。当前项目没有这些历史实验材料，因此更干净，但也少了问题复盘依据。

## 9. 风险与兼容性判断

1. 策略维度兼容：当前项目和 `agi_origin` 都是 12DOF、单帧观测 47，因此网络输入输出维度兼容。
2. 训练行为不等价：`agi_origin` 的 reference generation 和奖励函数已经改变，即使维度相同，学到的步态目标不同。
3. URDF 不同：当前项目用 `x1.urdf`，`agi_origin` 用 `X1_12DOF.urdf`，Isaac 训练的动力学模型可能不同。
4. `agi_origin` 的 `max_iterations = 50` 是明显短测设置，不能作为正式训练配置。
5. `agi_origin` 的 `play.py` 默认会渲染和写 CSV，运行成本和输出位置与当前项目不同。
6. `train_with_metrics.py` 中文注释在当前终端显示有编码乱码迹象，但 Python 逻辑本身可读；迁移前建议统一文件编码为 UTF-8 并实际运行自测。

## 10. 迁移建议

如果想从 `agi_origin` 合并有价值内容，建议拆成四类：

1. 可直接考虑迁移：`train_with_metrics.py`、`play.py` 中用 `env.feet_indices` 替代硬编码脚 index 的逻辑、CSV 诊断字段设计。
2. 需要谨慎验证：minimum-jerk + IK 的 `compute_ref_state()`，因为它会改变学习目标。
3. 可做 ablation 的奖励：`hip_yaw_roll_default`、`leg_symmetry`、`feet_clearance/feet_air_time` 提权。
4. 不建议直接迁移：`max_iterations = 50`、默认 `RENDER/LOG_CSV/FIX_COMMAND = True`，这些是调试设置。

## 11. 一句话判断

当前项目是干净的 12DOF X1 基线；`E:\agi_origin` 是同一 12DOF 路线上的实验诊断版，核心网络维度兼容，但训练目标、URDF、参考轨迹、奖励和评估脚本已经明显分叉。


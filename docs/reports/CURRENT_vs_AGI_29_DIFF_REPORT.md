# 当前项目 vs E:\agi_29 差异分析报告

生成时间：2026-06-30  
当前项目：`F:\agibot_x1_train`  
对比项目：`E:\agi_29`  
对比范围：排除 `.git` 内部对象；业务文件、资源文件、脚本和配置均纳入。  

## 1. 总体结论

`E:\agi_29` 不是当前 12DOF X1 项目的小修版，而是一次面向 `f1_29` 机器人资源的 29DOF 迁移版本。它把策略动作空间从 12 扩到 29，观测维度从单帧 47 扩到 100，特权观测从单帧 73 扩到 141，并同步改动了机器人资产、PD 控制、奖励权重、参考动作、播放脚本和 sim2sim 对齐逻辑。

当前项目更像稳定的 12DOF X1 训练基线：资源路径为 `resources/robots/x1`，地形默认 `trimesh`，随机化范围较强，训练迭代数更长。`agi_29` 更像 29DOF 扩展后的阶段训练版本：资源路径改为 `resources/robots/f1_29`，地形先降为 `plane`，随机化显著收窄，学习率大幅提高，并新增上半身/腿部分段动作缩放和上半身对称性奖励。

## 2. 版本与文件规模

| 项目 | 最近提交 | 文件数 | 总大小 | 主要差异 |
|---|---:|---:|---:|---|
| 当前项目 | `e6651b9 first commit` | 104 | 303.05 MB | 含 `docs/assets/` 图片/GIF；12DOF X1 资源 |
| `E:\agi_29` | `5d0d9b0 first commit` | 106 | 67.95 MB | 无对应媒体素材目录；使用 `f1_29` 机器人资源 |

文件哈希对比结果：

| 类别 | 数量 |
|---|---:|
| 同路径共同文件 | 30 |
| 同路径且内容一致 | 23 |
| 同路径但内容不同 | 7 |
| 仅当前项目存在 | 74 |
| 仅 `agi_29` 存在 | 76 |

同路径但内容不同的业务文件：

- `setup.py`
- `humanoid/algo/ppo/dh_on_policy_runner.py`
- `humanoid/envs/base/legged_robot.py`
- `humanoid/envs/x1/x1_dh_stand_config.py`
- `humanoid/envs/x1/x1_dh_stand_env.py`
- `humanoid/scripts/play.py`
- `humanoid/scripts/sim2sim.py`

同路径且内容一致的主要模块包括 README、utils、大部分 PPO 基础文件、训练入口 `train.py`、导出脚本等。

## 3. 资源与机器人模型差异

### 3.1 资源路径

| 项目 | URDF | MJCF |
|---|---|---|
| 当前项目 | `resources/robots/x1/urdf/x1.urdf` | `resources/robots/x1/mjcf/xyber_x1_flat.xml`，包含 `xyber_x1_serial.xml` |
| `agi_29` | `resources/robots/f1_29/urdf/f1_29dof.urdf` | `resources/robots/f1_29/mjcf/robot/xyber_x1/f1_29dof.xml` |

### 3.2 URDF / MJCF 规模

| 指标 | 当前项目 | `agi_29` | 影响 |
|---|---:|---:|---|
| URDF links | 58 | 65 | `agi_29` 增加头部、传感器、上半身相关 link |
| URDF joints | 57 | 64 | `agi_29` 关节总数更多 |
| URDF 可动关节 | 12 | 29 | 策略动作维度完全不同 |
| MJCF bodies | 30 | 35 | MuJoCo 模型结构不同 |
| MJCF hinge joints | 12 | 30 | `agi_29` MJCF 中含一个非 actuator hinge |
| MJCF actuators | 12 | 29 | 与 `env.num_actions = 29` 对齐 |

当前项目 12 个可动关节是双腿：

`left/right_hip_pitch`、`hip_roll`、`hip_yaw`、`knee_pitch`、`ankle_pitch`、`ankle_roll`

`agi_29` 29 个可动关节顺序为：

腰部 3 个、左臂 7 个、右臂 7 个、左腿 6 个、右腿 6 个。

### 3.3 STL 网格

`agi_29` 的大部分网格只是从 `x1/meshes` 迁移到 `f1_29/meshes`，哈希一致。按文件名映射后：

| 类别 | 数量 | 说明 |
|---|---:|---|
| 内容相同的映射网格 | 64 | 多数 STL 没有几何变化 |
| 内容不同的映射网格 | 1 | 当前 `lumber_pitch.STL` 对应 `agi_29/lumbar_pitch.stl`，内容不同 |
| `agi_29` 额外网格 | 7 | `Camera.stl`、`head.stl`、`head_face_bracket.stl`、`lumbar_pitch_f1.STL`、`neck_motor_base.stl`、`neck_motor_bracket.stl`、`radar.stl` |

另一个明显差异是命名：当前项目使用 `lumber_*` 拼写，`agi_29` 使用 `lumbar_*`。这不是单纯风格问题，URDF/MJCF 引用路径也随之改变。

## 4. 训练配置差异

核心配置文件：`humanoid/envs/x1/x1_dh_stand_config.py`

| 配置项 | 当前项目 | `agi_29` | 影响 |
|---|---:|---:|---|
| `num_actions` | 12 | 29 | 策略输出维度不同，模型不能互换 |
| `num_single_obs` | 47 | 100 | actor 输入单帧维度不同 |
| `frame_stack` | 66 | 66 | 堆叠帧数相同 |
| `num_observations` | 3102 | 6600 | actor 总输入维度不同 |
| `single_num_privileged_obs` | 73 | 141 | critic 单帧维度不同 |
| `c_frame_stack` | 3 | 3 | critic 堆叠数相同 |
| `num_privileged_obs` | 219 | 423 | critic 总输入维度不同 |
| `default_joint_angles` | 12 项 | 29 项 | 默认姿态从腿部扩展到腰、臂、腿 |
| `terrain.mesh_type` | `trimesh` | `plane` | `agi_29` 先在平地阶段训练 |
| `noise.noise_level` | 1.5 | 1.0 | `agi_29` 降低观测噪声 |
| `asset.foot_name` | `ankle_roll` | `ankle_roll_link` | 适配新模型 body 命名 |
| `asset.knee_name` | `knee_pitch` | `knee_pitch_link` | 同上 |

### 4.1 控制参数

当前项目只有腿部 PD 参数：

- `hip_pitch_joint: 30`
- `hip_roll_joint: 40`
- `hip_yaw_joint: 35`
- `knee_pitch_joint: 100`
- `ankle_pitch_joint: 35`
- `ankle_roll_joint: 35`
- `action_scale = 0.5`

`agi_29` 增加了上半身和分段缩放：

- 新增 `lumbar`、`shoulder`、`elbow`、`wrist`、`neck`、`head` 等 PD key
- 髋关节刚度提高，膝和踝部分参数重新平衡
- `action_scale = 0.5`
- `action_scale_upper = 0.1`
- `num_upper_body_joints = 17`

这意味着 `agi_29` 的动作不能按当前项目的统一 `action_scale` 解释，否则上半身会被放大。

### 4.2 Domain randomization

| 项目 | 当前项目 | `agi_29` | 解读 |
|---|---:|---:|---|
| `added_mass_range` | `[-3, 3]` | `[-1, 1]` | `agi_29` 降低质量扰动 |
| `motor_offset_range` | `[-0.035, 0.035]` | `[-0.01, 0.01]` | `agi_29` 降低电机偏移 |
| `joint_friction_range` | `[0.01, 1.15]` | `[0.0, 0.0]` | `agi_29` 暂时取消摩擦扰动 |
| `joint_damping_range` | `[0.3, 1.5]` | `[0.8, 1.2]` | `agi_29` 缩窄阻尼扰动 |
| `lag_timesteps_range` | `[5, 40]` | `[1, 5]` | `agi_29` 大幅降低控制延迟 |
| `dof_lag_timesteps_range` | `[0, 40]` | `[0, 5]` | 同上 |
| `randomize_coulomb_friction` | `True` | `False` | `agi_29` 关闭库仑摩擦随机化 |

`agi_29` 的随机化策略更偏“先学会 29DOF 平地基本运动”，当前项目则更偏“12DOF 稳健泛化”。

### 4.3 命令范围与步态参考

| 项目 | 当前项目 | `agi_29` |
|---|---:|---:|
| `lin_vel_x` | `[-0.4, 1.2]` | `[-0.5, 1.2]` |
| `lin_vel_y` | `[-0.4, 0.4]` | `[-0.3, 0.3]` |
| `ang_vel_yaw` | `[-0.6, 0.6]` | `[-0.6, 0.6]` |
| `cycle_time` | 0.7 | 0.6 |
| `target_feet_height` | 0.03 | 0.05 |
| `target_feet_height_max` | 0.06 | 0.10 |
| `final_swing_joint_delta_pos` | 12 项 | 29 项 |

`agi_29` 加快步频、提高摆腿高度，并把参考动作扩展到腰部、上肢和腿部。

## 5. 奖励函数与奖励权重差异

当前项目奖励函数数量为 30，`agi_29` 为 35。`agi_29` 新增：

- `_reward_upper_body_pos`
- `_reward_arm_swing_symmetry`
- `_reward_leg_swing_symmetry`
- `_reward_hip_yaw_symmetry`
- `_reward_torso_stability_symmetric`

关键权重变化：

| 奖励项 | 当前项目 | `agi_29` | 影响 |
|---|---:|---:|---|
| `tracking_lin_vel` | 1.8 | 5.0 | `agi_29` 明显强化速度跟踪 |
| `tracking_ang_vel` | 1.1 | 1.5 | 转向跟踪略增强 |
| `orientation` | 1.0 | 3.0 | 更重视躯干稳定 |
| `base_height` | 0.2 | 2.0 | 更重视高度 |
| `stand_still` | 2.5 | 1.0 | 降低静止偏好 |
| `feet_contact_forces` | -0.01 | -0.1 | 更强接触力惩罚 |
| `foot_slip` | -0.1 | -0.15 | 更强防滑 |
| `torques` | `-8e-9` | `-1e-6` | 能量惩罚增强很多 |
| `dof_vel` | `-2e-8` | `-3e-6` | 关节速度惩罚增强 |
| `action_smoothness` | -0.002 | -0.02 | 动作平滑惩罚增强 |
| `low_speed` | 0.2 | 0.0 | 移除低速辅助奖励 |
| `track_vel_hard` | 0.5 | 0.0 | 移除硬速度跟踪辅助 |

`agi_29` 的奖励设计更复杂：一方面强推速度跟踪、姿态和上半身协调，另一方面显著加强能量、冲击、速度和平滑惩罚。这套权重不适合直接搬回当前 12DOF 项目，除非同步处理动作维度和奖励函数依赖。

### 5.1 `agi_29` 新增奖励项解释

下面 5 个奖励项只存在于 `agi_29` 的 29DOF 全身模型中，当前 12DOF 项目没有启用。它们主要用于约束腰部、双臂和 29DOF 下的左右对称行为。

#### 5.1.1 `_reward_upper_body_pos`

作用：约束上半身大部分关节保持默认姿态，避免策略为了速度奖励让腰、肘、腕等关节乱摆。

它计算：

```text
joint_diff = dof_pos - default_joint_pd_target
reward = exp(-10 * selected_upper_body_diff^2_sum)
```

被约束的关节包括：

```text
腰部：0, 1, 2
左臂非 shoulder_pitch：4, 5, 6, 7, 8, 9
右臂非 shoulder_pitch：11, 12, 13, 14, 15, 16
```

它故意排除了 `left_shoulder_pitch_joint` 和 `right_shoulder_pitch_joint`，因为肩 pitch 摆动交给 `_reward_arm_swing_symmetry` 单独驱动。通俗理解：手臂可以前后摆，但其它上半身关节尽量保持自然默认姿态。

#### 5.1.2 `_reward_arm_swing_symmetry`

作用：让双臂跟随步态相位产生摆臂，同时限制肩关节不要漂到危险角度。

核心目标是：

```text
swing_target = 0.25 * sin(2*pi*phase)
```

奖励由四部分组成：

| 子项 | 权重 | 含义 |
|---|---:|---|
| `phase_reward` | 0.35 | 左右肩 pitch 接近相位目标 |
| `safe_reward` | 0.25 | 肩 pitch 超过 `0.5 rad` 后快速降分 |
| `anti_phase` | 0.20 | 左右肩 pitch 关系保持对称 |
| `vel_reward` | 0.20 | 鼓励手臂有摆动速度，避免完全静止 |

站立命令下该奖励归零，也就是站立时不鼓励摆臂，走路时才鼓励摆臂。

注意：代码注释写的是“反相对称”，但公式是 `left_pos - right_pos ≈ 0`。如果左右肩 pitch 的关节轴在 URDF/MJCF 中是镜像方向，这可能对应物理上的反相摆臂；如果关节轴方向相同，它实际会鼓励同向摆臂。继续使用前建议结合 `f1_29.urdf` 的肩关节 axis 确认。

#### 5.1.3 `_reward_leg_swing_symmetry`

作用：约束左右脚在机器人局部坐标系下保持横向对称，并在双支撑时保持高度接近。

它先把左右脚世界坐标转到 base 局部坐标系：

```text
feet_pos_local = quat_rotate_inverse(base_quat, feet_pos)
```

然后计算：

```text
横向对称：left_y + right_y ≈ 0
双支撑高度对称：left_z ≈ right_z
```

最终奖励：

```text
reward = 0.6 * lateral_symmetry + 0.4 * height_reward
```

其中高度对称只在双支撑期启用；单脚摆动时不强制左右脚等高，避免压制正常抬脚。通俗理解：左脚离身体中线多远，右脚也应镜像地离中线差不多远；双脚都支撑时，两只脚高度不要一高一低。

#### 5.1.4 `_reward_hip_yaw_symmetry`

作用：约束左右髋 yaw 镜像对称，减少外八、内八或左右脚朝向不一致。

它取：

```text
left_hip_yaw_idx = 19
right_hip_yaw_idx = 25
```

奖励公式：

```text
reward = exp(-10 * (left_hip_yaw + right_hip_yaw)^2)
```

目标是：

```text
left_hip_yaw ≈ -right_hip_yaw
```

这适用于左右髋 yaw 关节镜像设计的情况。通俗理解：左腿向外转多少，右腿也应镜像地向外转多少，而不是一只脚明显外八、另一只脚正常。

#### 5.1.5 `_reward_torso_stability_symmetric`

作用：约束躯干和腰部不要乱扭、乱甩、左右摇晃。

它由五部分组成：

| 子项 | 权重 | 含义 |
|---|---:|---|
| base yaw | 0.25 | 身体 yaw 角不要偏太大 |
| base yaw velocity | 0.15 | 不要快速左右扭身 |
| lumbar yaw | 0.20 | 腰部 yaw 关节不要乱转 |
| lumbar roll | 0.25 | 腰部 roll 不要侧弯 |
| base roll velocity | 0.15 | 不要快速左右摇晃 |

通俗理解：腿和手臂可以动，但躯干不要通过大幅扭腰、甩腰来投机获得速度或平衡奖励。

整体看，这 5 个奖励项是 `agi_29` 为 29DOF 全身控制新增的“形态约束”。它们不只是多了几项 reward，还隐含依赖 29DOF 的关节顺序、腰部关节、肩关节和足端刚体索引。直接移植到当前 12DOF 项目没有意义；如果迁移到另一个全身模型，需要先重新确认 DOF 索引和关节轴方向。

## 6. 环境实现差异

核心文件：`humanoid/envs/x1/x1_dh_stand_env.py`

主要变化：

1. `compute_ref_state()` 的腿部索引从当前项目的 `0-11` 改为 `17-28`，因为 `agi_29` 的前 17 个动作是腰部和双臂。
2. `agi_29` 给肩部和腰部也生成参考趋势：肩 pitch 跟随对侧腿相位，腰 pitch 使用 `lumbar_pitch_amp`。
3. `ref_action` 改为按上半身和下半身分段除以不同 scale，而不是当前项目的 `2 * ref_dof_pos`。
4. `agi_29` 覆盖 `_compute_torques()`，按关节段应用动作缩放：上半身小 scale，腿部使用 `action_scale`。
5. 观测新增 `sin_pos_diff` 和 `cos_pos_diff` 两个相位偏移特征。
6. 特权观测维度从 73 扩到 141，主要来自 29DOF 的 `dof_pos`、`dof_vel`、`actions`、`diff`。
7. `_reward_ref_joint_pos()` 在 `agi_29` 中只跟踪腿部，肩部摆臂交给新奖励项处理。
8. `_reward_feet_clearance()` 从二值区间奖励调整为高斯接近目标高度并惩罚超过最大高度。

潜在注意点：

- `agi_29` 在 `LeggedRobot._compute_torques()` 里有硬编码分段：`0:15`、`15:27`、`27:`。但配置中注释写上半身 17 个关节，环境 override 又使用 `:17` 与 `17:29`。这两个分段定义不完全一致，迁移或继续训练前应确认真实 DOF 顺序。
- `agi_29` 的 MJCF 统计为 30 个 hinge、29 个 actuator，说明有一个 hinge 可能不受策略直接驱动。sim2sim 和 Isaac Gym 的 DOF 顺序需要逐项校验。

## 7. 脚本差异

### 7.1 `play.py`

`agi_29` 的播放脚本更偏评估和录制：

- 默认 `RENDER = True`
- 默认 `FIX_COMMAND = True`
- 固定命令速度从当前项目的 `0.5` 改为 `1.0`
- 视频保存到 `/personal/train-more`
- 相机位置从 `(1, -1, 0.5)` 调整到 `(2.0, -2.0, 1.5)`
- 视频叠加速度、左右脚接触状态、双支撑/腾空状态文字
- 日志中的 `dof_pos_target` 按上半身/腿部/颈头不同 scale 计算

当前项目的 `play.py` 更朴素，默认不渲染、不固定命令，视频保存逻辑也保持原始工程风格。

### 7.2 `sim2sim.py`

`agi_29` 的 sim2sim 适配点：

- foot body 识别从宽泛条件改成 `ankle_roll_link`
- base body 识别改成 `base_link`
- 对 `env.add_stand_bool` 使用 `hasattr` 防御
- policy action 到 target q 的映射改为分段 scale
- PD gain 按 `default_joint_angles` 的顺序做匹配，避免 29DOF 顺序错位

当前项目的 sim2sim 假设 12DOF 且统一 action scale，不适合直接加载 `agi_29` 的策略。

### 7.3 `dh_on_policy_runner.py`

当前项目固定记录 47 维 observation 的均值/方差。`agi_29` 改为读取 `self.env.num_single_obs`，避免 100 维观测时 TensorBoard 日志截断。

### 7.4 `setup.py`

`agi_29` 多了依赖：

- `pygame`

这可能是给 joystick 或交互控制使用的。当前项目没有声明该依赖。

## 8. 当前项目独有内容

当前项目独有 `docs/assets/` 媒体素材：

- `docs/assets/id.jpg`
- `docs/assets/joy_map.jpg`
- `docs/assets/mujoco.gif`
- `docs/assets/play.gif`
- `docs/assets/train.gif`

这些文档资源体积较大，也是当前项目总大小远大于 `agi_29` 的主要原因。

当前项目独有的机器人资源集中在 `resources/robots/x1`，但多数网格与 `agi_29/f1_29` 对应文件相同，只是路径和命名不同。

## 9. 迁移建议

如果目标是把 `agi_29` 的能力合并回当前项目，需要按层处理：

1. 先确定是否真的要迁移到 29DOF。若当前训练任务仍是 12DOF，不应直接合并 `x1_dh_stand_config.py` 和 `x1_dh_stand_env.py`。
2. 若迁移 29DOF，必须同时迁移 URDF/MJCF、default_joint_angles、action scale、observation dimension、critic dimension、reward functions、sim2sim 和 play 脚本。
3. 校验 DOF 顺序，重点检查 `0:15/15:27/27:` 与 `:17/17:29` 这两套分段是否冲突。
4. `agi_29` 的随机化明显收窄，适合阶段一训练；若要部署鲁棒策略，后续应逐步恢复随机化。
5. `agi_29` 的奖励权重更激进，建议用 ablation 逐步打开新增奖励，而不是一次性迁入。

## 10. 一句话判断

当前项目是 12DOF X1 稳定训练基线；`E:\agi_29` 是 29DOF F1/扩展 X1 适配分支。两者策略、模型、观测和控制链路不兼容，不能只替换某个脚本或配置文件来混用。


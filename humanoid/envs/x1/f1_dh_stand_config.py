from .x1_dh_stand_config import X1DHStandCfg, X1DHStandCfgPPO


F1_DOF_NAMES = [
    "lumbar_yaw_joint",
    "lumbar_roll_joint",
    "lumbar_pitch_joint",
    "left_shoulder_pitch_joint",
    "left_shoulder_roll_joint",
    "left_shoulder_yaw_joint",
    "left_elbow_pitch_joint",
    "left_elbow_yaw_joint",
    "left_wrist_pitch_joint",
    "left_wrist_roll_joint",
    "right_shoulder_pitch_joint",
    "right_shoulder_roll_joint",
    "right_shoulder_yaw_joint",
    "right_elbow_pitch_joint",
    "right_elbow_yaw_joint",
    "right_wrist_pitch_joint",
    "right_wrist_roll_joint",
    "left_hip_pitch_joint",
    "left_hip_roll_joint",
    "left_hip_yaw_joint",
    "left_knee_pitch_joint",
    "left_ankle_pitch_joint",
    "left_ankle_roll_joint",
    "right_hip_pitch_joint",
    "right_hip_roll_joint",
    "right_hip_yaw_joint",
    "right_knee_pitch_joint",
    "right_ankle_pitch_joint",
    "right_ankle_roll_joint",
]

F1_LEG_JOINT_NAMES = [
    "left_hip_pitch_joint",
    "left_hip_roll_joint",
    "left_hip_yaw_joint",
    "left_knee_pitch_joint",
    "left_ankle_pitch_joint",
    "left_ankle_roll_joint",
    "right_hip_pitch_joint",
    "right_hip_roll_joint",
    "right_hip_yaw_joint",
    "right_knee_pitch_joint",
    "right_ankle_pitch_joint",
    "right_ankle_roll_joint",
]

F1_UPPER_BODY_JOINT_NAMES = [
    name for name in F1_DOF_NAMES if name not in F1_LEG_JOINT_NAMES
]


class F1DHStandCfg(X1DHStandCfg):
    class env(X1DHStandCfg.env):
        num_single_obs = 98
        num_observations = int(X1DHStandCfg.env.frame_stack * num_single_obs)
        single_num_privileged_obs = 141
        single_linvel_index = 121
        num_privileged_obs = int(X1DHStandCfg.env.c_frame_stack * single_num_privileged_obs)
        num_actions = 29
        leg_joint_names = F1_LEG_JOINT_NAMES
        ankle_joint_names = [
            "left_ankle_pitch_joint",
            "left_ankle_roll_joint",
            "right_ankle_pitch_joint",
            "right_ankle_roll_joint",
        ]
        upper_body_joint_names = F1_UPPER_BODY_JOINT_NAMES

    class asset(X1DHStandCfg.asset):
        file = "{LEGGED_GYM_ROOT_DIR}/model/urdf/F1_29DOF_perfect_mirrored.urdf"
        xml_file = "{LEGGED_GYM_ROOT_DIR}/model/mjcf/F1_29DOF_flat.xml"
        name = "f1"
        foot_name = "ankle_roll_link"
        knee_name = "knee_pitch_link"

    class init_state(X1DHStandCfg.init_state):
        pos = [0.0, 0.0, 0.625]
        default_joint_angles = {name: 0.0 for name in F1_DOF_NAMES}

    class control(X1DHStandCfg.control):
        stiffness = {
            "lumbar_yaw_joint": 60,
            "lumbar_roll_joint": 80,
            "lumbar_pitch_joint": 80,
            "shoulder_pitch_joint": 20,
            "shoulder_roll_joint": 20,
            "shoulder_yaw_joint": 15,
            "elbow_pitch_joint": 15,
            "elbow_yaw_joint": 10,
            "wrist_pitch_joint": 5,
            "wrist_roll_joint": 5,
            "hip_pitch_joint": 30,
            "hip_roll_joint": 40,
            "hip_yaw_joint": 35,
            "knee_pitch_joint": 100,
            "ankle_pitch_joint": 35,
            "ankle_roll_joint": 35,
        }
        damping = {
            "lumbar_yaw_joint": 6,
            "lumbar_roll_joint": 8,
            "lumbar_pitch_joint": 8,
            "shoulder_pitch_joint": 2,
            "shoulder_roll_joint": 2,
            "shoulder_yaw_joint": 1.5,
            "elbow_pitch_joint": 1.5,
            "elbow_yaw_joint": 1,
            "wrist_pitch_joint": 0.5,
            "wrist_roll_joint": 0.5,
            "hip_pitch_joint": 3,
            "hip_roll_joint": 3.0,
            "hip_yaw_joint": 4,
            "knee_pitch_joint": 10,
            "ankle_pitch_joint": 0.5,
            "ankle_roll_joint": 0.5,
        }
        action_scale = 0.5
        action_scale_by_joint = {
            "lumbar": 0.05,
            "shoulder": 0.05,
            "elbow": 0.05,
            "wrist": 0.05,
        }

    class rewards(X1DHStandCfg.rewards):
        class scales(X1DHStandCfg.rewards.scales):
            upper_body_zero = 0.3


class F1DHStandCfgPPO(X1DHStandCfgPPO):
    class policy(X1DHStandCfgPPO.policy):
        in_channels = F1DHStandCfg.env.frame_stack

    class algorithm(X1DHStandCfgPPO.algorithm):
        if F1DHStandCfg.terrain.measure_heights:
            lin_vel_idx = (F1DHStandCfg.env.single_num_privileged_obs + F1DHStandCfg.terrain.num_height) * (F1DHStandCfg.env.c_frame_stack - 1) + F1DHStandCfg.env.single_linvel_index
        else:
            lin_vel_idx = F1DHStandCfg.env.single_num_privileged_obs * (F1DHStandCfg.env.c_frame_stack - 1) + F1DHStandCfg.env.single_linvel_index

    class runner(X1DHStandCfgPPO.runner):
        experiment_name = "f1_dh_stand"

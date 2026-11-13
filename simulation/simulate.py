#!/usr/bin/env python3
"""Idealized two-wheel balancing simulation, not a hardware controller."""
import argparse
import json
from pathlib import Path
import time

import mujoco
import numpy as np


def run(seconds=10., pitch_deg=2., head_swing=.4, push_newtons=0.,
        viewer_enabled=False, control=True):
    if seconds <= 0 or abs(head_swing) > .7:
        raise ValueError('seconds must be positive and head swing <= 0.7 rad')
    model = mujoco.MjModel.from_xml_path(str(Path(__file__).with_name('robot.xml')))
    data = mujoco.MjData(model)
    quat = np.zeros(4)
    mujoco.mju_axisAngle2Quat(quat, np.array([0., 1., 0.]), np.deg2rad(pitch_deg))
    data.qpos[3:7] = quat
    mujoco.mj_forward(model, data)
    body_id = model.body('body').id
    viewer = None
    if viewer_enabled:
        from mujoco import viewer as mj_viewer
        viewer = mj_viewer.launch_passive(model, data)
    peak_roll = 0.
    peak_pitch = 0.
    peak_torque = 0.
    fell_at = None
    for _ in range(int(seconds / model.opt.timestep)):
        mat = data.xmat[body_id].reshape(3, 3)
        roll = np.arctan2(mat[2, 1], mat[2, 2])
        pitch = np.arctan2(-mat[2, 0], np.hypot(mat[2, 1], mat[2, 2]))
        # Ideal state-feedback only; not sampled IMU or a validated robot controller.
        torque = float(np.clip(4*pitch + .7*data.qvel[4] + .3*data.qpos[0]
                               + .3*data.qvel[0], -1.37, 1.37)) if control else 0.
        data.ctrl[:] = [torque, torque, head_swing*np.sin(2*np.pi*.5*data.time)]
        data.xfrc_applied[body_id, :] = 0
        if 2.0 <= data.time < 2.1:
            data.xfrc_applied[body_id, 0] = push_newtons
        mujoco.mj_step(model, data)
        peak_roll = max(peak_roll, abs(float(roll)))
        peak_pitch = max(peak_pitch, abs(float(pitch)))
        peak_torque = max(peak_torque, abs(torque))
        if fell_at is None and (abs(roll) > np.deg2rad(30) or abs(pitch) > np.deg2rad(30)):
            fell_at = float(data.time)
        if viewer is not None:
            if not viewer.is_running():
                break
            viewer.sync()
            time.sleep(model.opt.timestep)
    if viewer is not None:
        viewer.close()
    return {'seconds': round(float(data.time), 3),
            'max_roll_deg': round(float(np.degrees(peak_roll)), 3),
            'max_pitch_deg': round(float(np.degrees(peak_pitch)), 3),
            'fell_at_s': None if fell_at is None else round(fell_at, 3),
            'max_motor_torque_Nm': round(peak_torque, 4),
            'end_x_m': round(float(data.qpos[0]), 4),
            'push_N': push_newtons, 'head_amplitude_rad': head_swing,
            'feedback': 'ideal_state' if control else 'disabled'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=float, default=10)
    parser.add_argument('--pitch-deg', type=float, default=2)
    parser.add_argument('--head-swing', type=float, default=.4)
    parser.add_argument('--push-newtons', type=float, default=0)
    parser.add_argument('--viewer', action='store_true')
    parser.add_argument('--no-control', action='store_true')
    args = parser.parse_args()
    result = run(args.seconds, args.pitch_deg, args.head_swing, args.push_newtons,
                 args.viewer, not args.no_control)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print('Chỉ mô phỏng lý tưởng; không phải điều khiển đã xác minh cho robot thật.')


if __name__ == '__main__':
    main()

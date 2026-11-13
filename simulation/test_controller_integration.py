"""Exercise the Pi-independent controller against MuJoCo ideal state, never hardware."""
from pathlib import Path
import math
import sys
import unittest

import mujoco
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'software'))
from core import BalanceController, Config, Observation, State

class IntegrationTest(unittest.TestCase):
    def test_controller_with_ideal_mujoco_state(self):
        model = mujoco.MjModel.from_xml_path(str(Path(__file__).with_name('robot.xml')))
        data = mujoco.MjData(model)
        q = np.zeros(4)
        mujoco.mju_axisAngle2Quat(q, np.array([0., 1., 0.]), math.radians(2))
        data.qpos[3:7] = q
        mujoco.mj_forward(model, data)
        # Explicit simulation-only calibration, maps dimensionless output to 1.37 Nm.
        cfg = Config(kp=4*math.pi/180/1.37, kd=.7*math.pi/180/1.37,
                     kpos=.3/1.37, kv=.3/1.37, max_output=1,
                     calibrated=True, encoder_verified=True, watchdog_verified=True)
        controller = BalanceController(cfg)
        def observation():
            r = data.xmat[model.body('body').id].reshape(3, 3)
            pitch = math.degrees(math.atan2(-r[2,0], math.hypot(r[2,1], r[2,2])))
            return Observation(pitch, math.degrees(data.qvel[4]), data.qpos[0], data.qvel[0])
        controller.arm(observation())
        peak=0.
        for _ in range(2500):
            obs = observation()
            left, right = controller.step(obs, model.opt.timestep)
            self.assertEqual(controller.state, State.ARMED)
            data.ctrl[:] = (left*1.37, right*1.37, .4*math.sin(2*math.pi*.5*data.time))
            mujoco.mj_step(model, data)
            peak=max(peak, abs(obs.pitch_deg))
        self.assertLess(peak, 5.)

if __name__ == '__main__':
    unittest.main()

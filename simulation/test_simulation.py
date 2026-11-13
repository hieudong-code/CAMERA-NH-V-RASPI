"""Behavior checks: two physical disturbances and a negative control."""
import unittest
from simulate import run


class SimulationChecks(unittest.TestCase):
    def test_ideal_control_resists_small_pitch_and_head_motion(self):
        result = run(seconds=10, pitch_deg=2, head_swing=.4)
        self.assertIsNone(result['fell_at_s'], result)
        self.assertLess(result['max_pitch_deg'], 10, result)
        self.assertLess(abs(result['end_x_m']), .25, result)
        self.assertLessEqual(result['max_motor_torque_Nm'], 1.37)

    def test_ideal_control_resists_short_push(self):
        result = run(seconds=10, pitch_deg=2, head_swing=.4, push_newtons=1)
        self.assertIsNone(result['fell_at_s'], result)
        self.assertLess(result['max_pitch_deg'], 10, result)

    def test_unpowered_model_falls_from_initial_tilt(self):
        result = run(seconds=5, pitch_deg=2, head_swing=0, control=False)
        self.assertIsNotNone(result['fell_at_s'], result)


if __name__ == '__main__':
    unittest.main()

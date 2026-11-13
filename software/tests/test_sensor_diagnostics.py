"""Test physical sign consistency and fail-closed MPU range setup offline."""
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sensors import PitchFilter
from read_sensors import (configure_imu, PWR_MGMT_1, GYRO_CONFIG, ACCEL_CONFIG)

class PitchPhysicsTests(unittest.TestCase):
    def test_gyro_and_gravity_imply_same_positive_rotation(self):
        # A +Y rotation at +30 deg/s takes 0.02 s to reach +0.6 deg.
        # For gravity +Z at rest, sensor-frame specific force becomes -X.
        for sign in (1, -1):
            f = PitchFilter(sign=sign)
            f.update(0, 1, 0, .02)
            rad = math.radians(.6)
            pitch, rate = f.update(-math.sin(rad), math.cos(rad), 30, .02)
            self.assertAlmostEqual(pitch, sign * .6, places=10)
            self.assertAlmostEqual(rate, sign * 30, places=10)

class ImuConfigurationTests(unittest.TestCase):
    def test_configures_and_reads_back_range(self):
        pi = Mock()
        pi.i2c_write_byte_data.return_value = 0
        pi.i2c_read_byte_data.return_value = 0
        sleeper = Mock()
        configure_imu(pi, 7, sleeper)
        self.assertEqual(pi.i2c_write_byte_data.call_args_list,
                         [unittest.mock.call(7,PWR_MGMT_1,0),
                          unittest.mock.call(7,GYRO_CONFIG,0),
                          unittest.mock.call(7,ACCEL_CONFIG,0)])
        self.assertEqual(pi.i2c_read_byte_data.call_args_list,
                         [unittest.mock.call(7,GYRO_CONFIG),
                          unittest.mock.call(7,ACCEL_CONFIG)])
        sleeper.assert_called_once_with(.1)

    def test_failed_write_or_bad_range_fails_closed(self):
        for reads, writes in [([0x08], [0, 0]), ([0x80], [0, 0]), ([-1], [0, 0]), ([], [-1]),
                              ([0], [0, -1]), ([0, 0x10], [0, 0, 0]),
                              ([0], [0, 0, -1])]:
            pi = Mock()
            pi.i2c_write_byte_data.side_effect = writes
            pi.i2c_read_byte_data.side_effect = reads
            with self.assertRaises(RuntimeError):
                configure_imu(pi, 7, lambda _: None)

if __name__ == '__main__':
    unittest.main()

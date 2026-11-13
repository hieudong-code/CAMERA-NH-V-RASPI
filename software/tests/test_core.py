import math
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from core import BalanceController, Config, Observation, State
from sensors import PitchFilter, Quadrature
import motor_hardware

READY=Config(kp=.03,kd=.003,calibrated=True,encoder_verified=True,watchdog_verified=True)
ZERO=Observation(0,0,0,0)

class BalanceTests(unittest.TestCase):
    def test_default_is_inert_and_cannot_arm(self):
        c=BalanceController(Config())
        self.assertEqual(c.step(Observation(1,0,0,0),.01),(0,0))
        with self.assertRaises(RuntimeError): c.arm(ZERO)
    def test_arm_and_output_saturation(self):
        c=BalanceController(READY); c.arm(ZERO)
        self.assertEqual(c.step(Observation(1,0,0,0),.01),(.03,.03))
        self.assertEqual(c.step(Observation(10,0,0,0),.01),(.25,.25))
    def test_excessive_tilt_latches(self):
        c=BalanceController(READY); c.arm(ZERO)
        self.assertEqual(c.step(Observation(15,0,0,0),.01),(0,0))
        self.assertEqual(c.state,State.FAULT)
        with self.assertRaises(RuntimeError): c.arm(ZERO)
    def test_stale_or_nan_causes_fault(self):
        for obs,dt in ((Observation(math.nan,0,0,0),.01),(ZERO,.031),(ZERO,math.nan)):
            c=BalanceController(READY); c.arm(ZERO)
            self.assertEqual(c.step(obs,dt),(0,0)); self.assertEqual(c.state,State.FAULT)
    def test_fault_does_not_restart_on_valid_data(self):
        c=BalanceController(READY); c.arm(ZERO); c.step(ZERO,.1)
        self.assertEqual(c.step(ZERO,.01),(0,0)); self.assertEqual(c.state,State.FAULT)
    def test_bad_gains_or_flags_rejected(self):
        for cfg in (Config(kp=-1),Config(kp=math.nan),Config(max_tilt_deg=100)):
            with self.assertRaises(ValueError): BalanceController(cfg)
        with self.assertRaises(RuntimeError): BalanceController(Config(kp=1,kd=1)).arm(ZERO)
    def test_all_hardware_drive_is_blocked(self):
        with self.assertRaises(RuntimeError): motor_hardware.set_motors(.1,.1)

class SensorTests(unittest.TestCase):
    def test_encoder_complete_cycle_and_reverse(self):
        q=Quadrature()
        for pair in [(0,1),(1,1),(1,0),(0,0)]: q.update(*pair)
        self.assertEqual(q.count,4)
        for pair in [(1,0),(1,1),(0,1),(0,0)]: q.update(*pair)
        self.assertEqual(q.count,0); self.assertEqual(q.invalid,0)
    def test_illegal_transition_recorded(self):
        q=Quadrature(); q.update(1,1)
        self.assertEqual(q.invalid,1); self.assertEqual(q.count,0)
    def test_filter_requires_finite_acceleration(self):
        f=PitchFilter()
        a,r=f.update(0,1,0,.01); self.assertAlmostEqual(a,0); self.assertAlmostEqual(r,0)
        with self.assertRaises(ValueError): f.update(0,0,0,.01)
        with self.assertRaises(ValueError): f.update(math.nan,1,0,.01)
        with self.assertRaises(ValueError): f.update(0,1,0,1)

if __name__=='__main__': unittest.main()

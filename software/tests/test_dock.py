import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from dock import Action, DockPlanner, Sensors, State


def snap(t, **overrides):
    values = dict(observed_at=t, battery_low=True, marker_visible=False,
                  obstacle_clear=True, contact=False, charging=False)
    values.update(overrides)
    return Sensors(**values)


class DockTests(unittest.TestCase):
    def setUp(self):
        self.planner = DockPlanner()

    def begin_search(self):
        p = self.planner
        self.assertEqual(p.step(0, snap(0)).state, State.RETURN_REQUESTED)
        self.assertEqual(p.step(.1, snap(.1)).state, State.SEARCH)

    def begin_approach(self):
        self.begin_search()
        p = self.planner
        self.assertEqual(p.step(.2, snap(.2, marker_visible=True)).state, State.APPROACH)

    def test_entire_plan_uses_symbolic_outputs(self):
        self.begin_search()
        p = self.planner
        self.assertEqual(p.step(.2, snap(.2)).action, Action.SCAN_PLAN)
        self.assertEqual(p.step(.3, snap(.3, marker_visible=True)).state, State.APPROACH)
        self.assertEqual(p.step(.4, snap(.4, marker_visible=True)).action, Action.APPROACH_PLAN)
        self.assertEqual(p.step(.5, snap(.5, contact=True)).state, State.CONTACT)
        self.assertEqual(p.step(.6, snap(.6, contact=True)).action, Action.STOP)
        self.assertEqual(p.step(.7, snap(.7, contact=True, charging=True)).state, State.CHARGING)
        self.assertEqual(p.step(.8, snap(.8, contact=True, charging=True)).action, Action.STOP)

    def test_idle_needs_fresh_battery_contact_and_charging_data(self):
        self.assertEqual(self.planner.step(0, Sensors(0, battery_low=True)).state, State.IDLE)
        self.assertEqual(self.planner.step(1, snap(0)).action, Action.STOP)
        self.assertEqual(self.planner.step(2, snap(2, battery_low=False)).state, State.IDLE)

    def test_manual_request_when_battery_is_not_low(self):
        self.assertEqual(self.planner.step(0, snap(0, battery_low=False), request_return=True).state,
                         State.RETURN_REQUESTED)

    def test_obstacle_or_unknown_sensor_stops_and_stale_stops(self):
        self.begin_approach()
        p = self.planner
        self.assertEqual(p.step(.3, snap(.3, marker_visible=True, obstacle_clear=False)).action, Action.STOP)
        self.assertEqual(p.step(.4, snap(.4, marker_visible=True, obstacle_clear=None)).action, Action.STOP)
        self.assertEqual(p.step(.5, snap(.5, marker_visible=True, contact=None)).action, Action.STOP)
        self.assertEqual(p.step(1.1, snap(.5, marker_visible=True)).action, Action.STOP)

    def test_lost_marker_returns_to_search_without_command(self):
        self.begin_approach()
        result = self.planner.step(.3, snap(.3, marker_visible=False))
        self.assertEqual((result.state, result.action), (State.SEARCH, Action.STOP))

    def test_timeout_while_missing_sensors_faults(self):
        self.begin_search()
        p = self.planner
        self.assertEqual(p.step(1, Sensors(None)).action, Action.STOP)
        self.assertEqual(p.step(31, Sensors(None)).state, State.FAULT)
        self.assertEqual(p.step(32, snap(32)).state, State.FAULT)

    def test_contact_loss_retries_are_bounded(self):
        self.begin_search()
        p = self.planner
        for n in range(3):
            t = 1 + 2*n
            self.assertEqual(p.step(t, snap(t, contact=True)).state, State.CONTACT)
            plan = p.step(t+.1, snap(t+.1, contact=False))
            self.assertEqual(plan.action, Action.STOP)
        self.assertEqual(plan.state, State.FAULT)
        self.assertEqual(plan.attempts, 3)

    def test_false_charging_confirmation_faults_and_loss_faults(self):
        plan = self.planner.step(0, snap(0, charging=True, contact=False))
        self.assertEqual(plan.state, State.FAULT)
        p = DockPlanner()
        self.assertEqual(p.step(0, snap(0, contact=True, charging=True)).state, State.CHARGING)
        self.assertEqual(p.step(.1, snap(.1, contact=True, charging=False)).state, State.FAULT)

    def test_invalid_time_or_malformed_sensor_values_fail_closed(self):
        self.assertEqual(self.planner.step(0, snap(0, obstacle_clear='yes')).action, Action.STOP)
        self.begin_search()
        self.assertEqual(self.planner.step(-1, snap(-1)).state, State.FAULT)

    def test_bad_configuration_rejected(self):
        with self.assertRaises(ValueError):
            DockPlanner(search_timeout=0)
        with self.assertRaises(ValueError):
            DockPlanner(max_snapshot_age=float('nan'))


if __name__ == '__main__':
    unittest.main()

"""Kế hoạch mô phỏng trạm sạc. KHÔNG điều khiển động cơ hay nguồn điện.

Mọi đầu vào là một ảnh chụp cảm biến có timestamp đơn điệu. Đầu ra là nhãn
biểu tượng để ghi log/mô phỏng, không có giao tiếp GPIO, mạng hay phần cứng.
Trạm tự hành ngoài đời còn cần camera, nhận dạng, cảm biến, bộ điều khiển
và kiểm thử thực tế; mô-đun này không triển khai các phần đó.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class State(str, Enum):
    IDLE = "idle"
    RETURN_REQUESTED = "return_requested"
    SEARCH = "search"
    APPROACH = "approach"
    CONTACT = "contact"
    CHARGING = "charging"
    FAULT = "fault"


class Action(str, Enum):
    STOP = "STOP"
    SCAN_PLAN = "SCAN_PLAN"
    APPROACH_PLAN = "APPROACH_PLAN"


@dataclass(frozen=True)
class Sensors:
    """None = thiếu dữ liệu. Các giá trị là ảnh chụp cùng một thời điểm."""
    observed_at: Optional[float]
    battery_low: Optional[bool] = None
    marker_visible: Optional[bool] = None
    obstacle_clear: Optional[bool] = None
    contact: Optional[bool] = None
    charging: Optional[bool] = None


@dataclass(frozen=True)
class Plan:
    state: State
    action: Action
    reason: str
    attempts: int


class DockPlanner:
    """Máy trạng thái dry-run, tuyệt đối không xuất xung động cơ."""

    def __init__(self, *, max_snapshot_age: float = 0.5,
                 search_timeout: float = 30.0, approach_timeout: float = 15.0,
                 contact_timeout: float = 10.0, max_retries: int = 2):
        durations = (max_snapshot_age, search_timeout, approach_timeout, contact_timeout)
        if any(not math.isfinite(x) or x <= 0 for x in durations) or max_retries < 0:
            raise ValueError("Invalid timeout or retry limit")
        self.max_snapshot_age = max_snapshot_age
        self.search_timeout = search_timeout
        self.approach_timeout = approach_timeout
        self.contact_timeout = contact_timeout
        self.max_retries = max_retries
        self.state = State.IDLE
        self.attempts = 0
        self._entered_at: Optional[float] = None
        self._last_now: Optional[float] = None

    def _enter(self, state: State, now: float) -> None:
        self.state, self._entered_at = state, now

    def _plan(self, action: Action, reason: str) -> Plan:
        return Plan(self.state, action, reason, self.attempts)

    def _fault(self, now: float, reason: str) -> Plan:
        self._enter(State.FAULT, now)
        return self._plan(Action.STOP, reason)

    def step(self, now: float, sensors: Sensors, *, request_return: bool = False) -> Plan:
        if (isinstance(now, bool) or not isinstance(now, (int, float)) or
                not math.isfinite(now) or (self._last_now is not None and now < self._last_now)):
            return self._fault(self._last_now or 0.0, "invalid monotonic time")
        self._last_now = now
        if self.state == State.FAULT:
            return self._plan(Action.STOP, "fault latched; manual reset required")
        if self._entered_at is None:
            self._entered_at = now

        deadline = {
            State.RETURN_REQUESTED: self.search_timeout,
            State.SEARCH: self.search_timeout,
            State.APPROACH: self.approach_timeout,
            State.CONTACT: self.contact_timeout,
        }.get(self.state)
        if deadline is not None and now - self._entered_at >= deadline:
            return self._fault(now, "state timeout")

        stamp = sensors.observed_at
        if (isinstance(stamp, bool) or not isinstance(stamp, (int, float)) or
                not math.isfinite(stamp) or stamp > now or now - stamp > self.max_snapshot_age):
            return self._plan(Action.STOP, "sensor snapshot missing or stale")
        for value in (sensors.battery_low, sensors.marker_visible, sensors.obstacle_clear,
                      sensors.contact, sensors.charging):
            if value is not None and type(value) is not bool:
                return self._plan(Action.STOP, "invalid sensor value")
        if sensors.battery_low is None or sensors.contact is None or sensors.charging is None:
            return self._plan(Action.STOP, "battery/contact/charging data missing")
        if sensors.charging and not sensors.contact:
            return self._fault(now, "charging reported without dock contact")

        if self.state == State.IDLE:
            if sensors.contact and sensors.charging:
                self._enter(State.CHARGING, now)
                return self._plan(Action.STOP, "already charging")
            if sensors.battery_low or request_return:
                self._enter(State.RETURN_REQUESTED, now)
                return self._plan(Action.STOP, "return requested")
            return self._plan(Action.STOP, "idle")

        if self.state == State.CHARGING:
            if not sensors.contact or not sensors.charging:
                return self._fault(now, "charging/contact lost; completion not modeled")
            return self._plan(Action.STOP, "charging monitored")

        if self.state == State.CONTACT:
            if not sensors.contact:
                self.attempts += 1
                if self.attempts > self.max_retries:
                    return self._fault(now, "retry limit exceeded")
                self._enter(State.SEARCH, now)
                return self._plan(Action.STOP, "contact lost; retry")
            if sensors.charging:
                self._enter(State.CHARGING, now)
                return self._plan(Action.STOP, "charging confirmed")
            return self._plan(Action.STOP, "waiting for charging confirmation")

        if sensors.contact:
            self._enter(State.CONTACT, now)
            return self._plan(Action.STOP, "dock contact detected")
        if sensors.marker_visible is None or sensors.obstacle_clear is None:
            return self._plan(Action.STOP, "vision/obstacle data missing")
        if not sensors.obstacle_clear:
            return self._plan(Action.STOP, "obstacle detected")
        if self.state == State.RETURN_REQUESTED:
            self._enter(State.SEARCH, now)
            return self._plan(Action.STOP, "search initialized")
        if self.state == State.SEARCH:
            if sensors.marker_visible:
                self._enter(State.APPROACH, now)
                return self._plan(Action.STOP, "marker detected")
            return self._plan(Action.SCAN_PLAN, "symbolic scan only")
        if self.state == State.APPROACH:
            if not sensors.marker_visible:
                self._enter(State.SEARCH, now)
                return self._plan(Action.STOP, "marker lost")
            return self._plan(Action.APPROACH_PLAN, "symbolic approach only")
        return self._fault(now, "unknown state")

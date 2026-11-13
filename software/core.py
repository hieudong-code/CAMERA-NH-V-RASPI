"""Safety-first balance loop. Gains are uncalibrated; never deploy without bench validation."""
from dataclasses import dataclass
from enum import Enum
import math

class State(Enum):
    DISARMED = 'DISARMED'
    ARMED = 'ARMED'
    FAULT = 'FAULT'

@dataclass(frozen=True)
class Config:
    kp: float = 0.0
    kd: float = 0.0
    kv: float = 0.0
    kpos: float = 0.0
    max_tilt_deg: float = 15.0
    max_period_s: float = 0.03
    max_output: float = 0.25
    calibrated: bool = False
    encoder_verified: bool = False
    watchdog_verified: bool = False

@dataclass(frozen=True)
class Observation:
    pitch_deg: float
    rate_dps: float
    position_m: float
    velocity_mps: float

class BalanceController:
    def __init__(self, cfg: Config):
        values = (cfg.kp, cfg.kd, cfg.kv, cfg.kpos, cfg.max_tilt_deg, cfg.max_period_s, cfg.max_output)
        if not all(math.isfinite(v) for v in values): raise ValueError('Non-finite configuration')
        if cfg.kp < 0 or cfg.kd < 0 or cfg.kv < 0 or cfg.kpos < 0: raise ValueError('Gains must be nonnegative; hardware polarity is set separately')
        if not (0 < cfg.max_tilt_deg <= 30 and 0 < cfg.max_period_s <= .1 and 0 < cfg.max_output <= 1):
            raise ValueError('Unsafe bounds')
        self.cfg, self.state, self.reason = cfg, State.DISARMED, ''

    def arm(self, obs: Observation):
        if self.state is State.FAULT: raise RuntimeError('Fault is latched; restart while safely supported')
        if not all((self.cfg.calibrated, self.cfg.encoder_verified, self.cfg.watchdog_verified)):
            raise RuntimeError('Calibration, encoder validation, and independent hardware watchdog are required')
        if self.cfg.kp <= 0 or self.cfg.kd <= 0: raise RuntimeError('Gains are not configured')
        if not self.valid(obs) or abs(obs.pitch_deg) > 5: raise RuntimeError('Robot must be supported near upright')
        self.state = State.ARMED

    @staticmethod
    def valid(obs: Observation):
        return all(math.isfinite(v) for v in (obs.pitch_deg, obs.rate_dps, obs.position_m, obs.velocity_mps))

    def fail(self, reason):
        self.state, self.reason = State.FAULT, reason
        return 0.0, 0.0

    def step(self, obs: Observation, dt: float):
        if self.state is not State.ARMED: return 0.0, 0.0
        if not self.valid(obs): return self.fail('imu_or_encoder_invalid')
        if not math.isfinite(dt) or dt <= 0 or dt > self.cfg.max_period_s: return self.fail('deadline_missed')
        if abs(obs.pitch_deg) >= self.cfg.max_tilt_deg: return self.fail('tilt_limit')
        c = self.cfg
        u = c.kp * obs.pitch_deg + c.kd * obs.rate_dps + c.kv * obs.velocity_mps + c.kpos * obs.position_m
        u = max(-c.max_output, min(c.max_output, u))
        return u, u

"""Pure transformations used by the diagnostic sensor reader; no GPIO access."""
import math

# Forward transition order; reverse direction is the reverse sequence.
_TRANSITIONS = {(0,1):1,(1,3):1,(3,2):1,(2,0):1,
                (1,0):-1,(3,1):-1,(2,3):-1,(0,2):-1}

class Quadrature:
    def __init__(self, a=0, b=0):
        self.state=(int(a)<<1)|int(b); self.count=0; self.invalid=0
    def update(self, a, b):
        new=(int(a)<<1)|int(b)
        if new != self.state:
            delta=_TRANSITIONS.get((self.state,new))
            if delta is None: self.invalid += 1
            else: self.count += delta
        self.state=new

class PitchFilter:
    """Tilt about sensor +Y, in degrees.

    Assumes upright specific force is +Z, and +Y rotation gives -X specific
    force. Mounting must align sensor axes; ``sign`` only reverses the result,
    it does not compensate for an arbitrary rotated IMU.
    """
    def __init__(self, sign=1, offset_deg=0.0, gyro_offset_dps=0.0, alpha=.98):
        if sign not in (-1,1) or not 0 <= alpha <= 1: raise ValueError('Bad filter configuration')
        self.sign,self.offset,self.gyro_offset,self.alpha=sign,offset_deg,gyro_offset_dps,alpha
        self.angle=None
    def update(self, ax, az, gyro_y, dt):
        if not all(math.isfinite(v) for v in (ax,az,gyro_y,dt)) or dt <= 0 or dt > .2:
            raise ValueError('Bad IMU reading or timing')
        if math.hypot(ax,az) < .1: raise ValueError('Accelerometer unavailable')
        accel=self.sign*math.degrees(math.atan2(-ax,az))-self.offset
        rate=self.sign*(gyro_y-self.gyro_offset)
        self.angle=accel if self.angle is None else self.alpha*(self.angle+rate*dt)+(1-self.alpha)*accel
        return self.angle,rate

"""Deterministic hardware-free control demonstration; not a physics simulation."""
from core import BalanceController, Config, Observation

def main():
    c=BalanceController(Config(kp=.03,kd=.003,calibrated=True,encoder_verified=True,watchdog_verified=True))
    c.arm(Observation(0,0,0,0))
    for angle in (0,1,2,1,0,16):
        outputs=c.step(Observation(angle,0,0,0),.01)
        print(f'{c.state.value}: angle={angle:+} deg -> simulated PWM={outputs}; reason={c.reason or "-"}')
    print('Demo only: imaginary sensor readings, no motor output.')
if __name__=='__main__': main()

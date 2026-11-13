"""Read-only sensor diagnostic for Raspberry Pi 4. It does not configure motor pins."""
import argparse, json, time
from pathlib import Path
from threading import Lock
from sensors import Quadrature, PitchFilter

LEFT=(17,27); RIGHT=(22,23)
def signed(hi,lo):
    value=(hi<<8)|lo
    return value-65536 if value & 0x8000 else value

# MPU-6050 register addresses and full-scale fields.
PWR_MGMT_1 = 0x6B
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
CONFIG_CONTROL_MASK = 0xF8  # self-test bits plus full-scale bits

def configure_imu(pi, handle, sleeper=time.sleep):
    """Wake MPU-6050, select ±2g/±250 dps, and verify both settings.

    We deliberately refuse to decode raw samples if configuration cannot be
    read back: the fixed conversion factors below assume these full scales.
    """
    if pi.i2c_write_byte_data(handle, PWR_MGMT_1, 0) < 0:
        raise RuntimeError('Cannot wake IMU')
    sleeper(0.1)
    for register in (GYRO_CONFIG, ACCEL_CONFIG):
        if pi.i2c_write_byte_data(handle, register, 0) < 0:
            raise RuntimeError(f'Cannot configure IMU register 0x{register:02x}')
        value = pi.i2c_read_byte_data(handle, register)
        if value < 0 or value & CONFIG_CONTROL_MASK:
            raise RuntimeError(f'IMU range/self-test verification failed at 0x{register:02x}')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config',default=str(Path(__file__).with_name('config.example.json')))
    p.add_argument('--seconds',type=float,default=10)
    args=p.parse_args()
    if not 0 < args.seconds <= 3600: p.error('seconds must be 0..3600')
    with open(args.config, encoding='utf-8') as f: h=json.load(f)['hardware']
    try: import pigpio
    except ImportError: raise SystemExit('Missing pigpio Python package/daemon; see README.')
    pi=pigpio.pi()
    if not pi.connected: raise SystemExit('Cannot connect to pigpiod.')
    handle=None; callbacks=[]; lock=Lock()
    try:
        for pin in (*LEFT,*RIGHT):
            pi.set_mode(pin,pigpio.INPUT)
            # Configure suitable external bias; encoder outputs must be 3.3 V compatible.
            pi.set_pull_up_down(pin,pigpio.PUD_OFF)
        left=Quadrature(pi.read(LEFT[0]),pi.read(LEFT[1]))
        right=Quadrature(pi.read(RIGHT[0]),pi.read(RIGHT[1]))
        def make_callback(pins, decoder):
            def on_edge(gpio,level,tick):
                if level not in (0,1): return
                with lock:
                    a=(decoder.state >> 1) & 1
                    b=decoder.state & 1
                    if gpio == pins[0]: a=level
                    else: b=level
                    decoder.update(a,b)
            return on_edge
        for pins,decoder in ((LEFT,left),(RIGHT,right)):
            cb=make_callback(pins,decoder)
            for pin in pins: callbacks.append(pi.callback(pin,pigpio.EITHER_EDGE,cb))
        handle=pi.i2c_open(1,int(h['imu_address']))
        if handle < 0: raise RuntimeError('Cannot open IMU')
        configure_imu(pi, handle)
        filt=PitchFilter(h['pitch_axis_sign'],h['pitch_offset_deg'],h['gyro_y_offset_dps'])
        deadline=time.monotonic()+args.seconds; last=time.monotonic(); shown=0
        while time.monotonic()<deadline:
            now=time.monotonic(); dt=now-last; last=now
            count,raw=pi.i2c_read_i2c_block_data(handle,0x3B,14)
            if count!=14: raise RuntimeError('Short IMU read; stop')
            ax=signed(raw[0],raw[1])/16384.0; az=signed(raw[4],raw[5])/16384.0
            gy=signed(raw[10],raw[11])/131.0
            angle,rate=filt.update(ax,az,gy,max(dt,.001))
            if now>=shown:
                with lock: print(f'pitch={angle:+.1f} deg rate={rate:+.1f} deg/s left={left.count} right={right.count} invalid={left.invalid}/{right.invalid}')
                shown=now+.25
            time.sleep(.01)
    finally:
        for cb in callbacks: cb.cancel()
        if handle is not None and handle >= 0: pi.i2c_close(handle)
        pi.stop()

if __name__=='__main__': main()

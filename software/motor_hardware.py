"""Hardware output lock. A validated independent watchdog and e-stop are not supplied."""
def set_motors(left: float, right: float):
    raise RuntimeError('Motor hardware output is disabled: watchdog, electrical safety, calibration and real-time behaviour have not been validated. Use simulation only.')

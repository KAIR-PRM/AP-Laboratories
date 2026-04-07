class PID:
    def __init__(self, Kp: float, Ki: float, Kd: float):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.integralValue = 0.0
        self.previousError = 0.0

    def step(self, error: float, dt: float):
        self.integralValue += error * dt

        if dt > 0:
            derivative = (error - self.previousError) / dt
        else:
            derivative = 0

        self.previousError = error

        return self.Kp * error + self.Ki * self.integralValue + self.Kd * derivative

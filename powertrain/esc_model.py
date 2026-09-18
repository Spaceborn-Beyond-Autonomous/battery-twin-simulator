"""
ESC (Electronic Speed Controller) Model (BTS-B - Day 3)

Simulates the ESC's role between the battery and the motor:
- Converts throttle signal (PWM) into an effective voltage for the motor
- Applies switching losses (ESC is not 100% efficient)
- Enforces current limits for protection
"""

from powertrain.powertrain_config import ESCSpec


class ESC:
    def __init__(self, spec: ESCSpec = None):
        self.spec = spec or ESCSpec()

    def process(self, battery_voltage: float, throttle_percent: float,
                motor_current: float) -> dict:
        if not (0 <= throttle_percent <= 100):
            raise ValueError("throttle_percent must be 0-100")

        pwm_duty_cycle = throttle_percent / 100.0

        raw_voltage = battery_voltage * pwm_duty_cycle
        effective_voltage = raw_voltage * self.spec.switching_efficiency

        # Power loss comes ONLY from switching inefficiency,
        # not from the duty-cycle voltage reduction (which is
        # normal voltage regulation, not a loss).
        input_power = raw_voltage * motor_current
        output_power = effective_voltage * motor_current
        esc_power_loss = max(input_power - output_power, 0.0)

        current_limited = motor_current > self.spec.max_current
        limited_current = min(motor_current, self.spec.max_current)

        return {
            "pwm_duty_cycle": round(pwm_duty_cycle, 3),
            "effective_voltage_v": round(effective_voltage, 3),
            "esc_power_loss_w": round(esc_power_loss, 3),
            "current_limited": current_limited,
            "limited_current_a": round(limited_current, 3),
        }


if __name__ == "__main__":
    esc = ESC()

    print("Test 1: 22.2V battery, 25% throttle, 0.5A motor current")
    print(esc.process(battery_voltage=22.2, throttle_percent=25.0, motor_current=0.5))

    print("\nTest 2: 22.2V battery, 100% throttle, 20A motor current")
    print(esc.process(battery_voltage=22.2, throttle_percent=100.0, motor_current=20.0))

    print("\nTest 3: Overcurrent case - 35A motor current (exceeds ESC max)")
    print(esc.process(battery_voltage=22.2, throttle_percent=100.0, motor_current=35.0))

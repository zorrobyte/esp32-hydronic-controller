import config
import time
import main
from logic import tempSensors


def state_message(state, message):
    print(f"[Current Startup Procedure: - {state}] {message}")


def start_up():
    state = "INIT_SYSTEM"
    step = 1
    exhaust_temps = []
    initial_exhaust_temp = None
    fan_speed_percentage = 20
    last_time_checked = time.time()
    glow_plug_heat_up_end_time = last_time_checked + 60
    startup_start_time = last_time_checked
    startup_time_limit = 300  # 5 minutes in seconds

    while True:
        current_time = time.time()
        config.heartbeat = current_time
        main.wdt.feed()

        if current_time - startup_start_time > startup_time_limit:
            state_message("TIMEOUT", "Startup took too long. Changing state to STOPPING.")
            config.startup_successful = False
            return

        if state == "INIT_SYSTEM":
            state_message(state, "Initializing system...")
            config.startup_successful = False  # Assume startup will fail
            initial_exhaust_temp = tempSensors.read_exhaust_temp()
            if initial_exhaust_temp > 100:
                state_message(state, "Initial exhaust temperature too high. Changing state to STOPPING.")
                config.startup_successful = False
                return
            fan_duty = int((fan_speed_percentage / 100) * 1023)
            config.air_pwm.duty(fan_duty)
            config.GLOW_PIN.on()
            state_message(state, f"Fan: {fan_speed_percentage}%, Glow plug: On")
            state = "INITIAL_FUELING"

        elif state == "INITIAL_FUELING":
            # state_message(state, "Waiting for glow plug to heat up...")
            if current_time >= glow_plug_heat_up_end_time:
                config.pump_frequency = 1
                state_message(state, f"Fuel Pump: {config.pump_frequency} Hz")
                state = "RAMPING_UP"
                last_time_checked = current_time
                exhaust_temps = []

        elif state == "RAMPING_UP":
            if current_time - last_time_checked >= 1:
                last_time_checked = current_time
                exhaust_temps.append(tempSensors.read_exhaust_temp())

                if len(exhaust_temps) >= 20:
                    avg_exhaust_temp = sum(exhaust_temps) / len(exhaust_temps)
                    state_message(state, f"Average Exhaust Temp at step {step}: {avg_exhaust_temp}C")

                    if avg_exhaust_temp >= 100:
                        state_message("COMPLETED", "Reached target exhaust temperature. Startup Procedure Completed.")
                        config.startup_successful = True
                        config.startup_attempts = 0
                        config.GLOW_PIN.off()
                        return

                    elif initial_exhaust_temp + 5 < avg_exhaust_temp:
                        fan_speed_percentage = min(fan_speed_percentage + 20, 100)
                        fan_duty = int((fan_speed_percentage / 100) * 1023)
                        config.air_pwm.duty(fan_duty)
                        config.pump_frequency = min(config.pump_frequency + 1, 5)
                        state_message(state,
                                      f"Step {step} successful. Fan: {fan_speed_percentage}%, Fuel Pump: {config.pump_frequency} Hz")
                        initial_exhaust_temp = avg_exhaust_temp
                        step += 1

                        if step > 5:
                            state_message("COMPLETED", "Startup Procedure Completed")
                            config.startup_successful = True
                            config.startup_attempts = 0
                            return

                        exhaust_temps = []
                    else:
                        state_message(state, "Temperature not rising as expected. Changing state to STOPPING.")
                        config.current_state = 'STOPPING'
                        config.startup_attempts += 1
                        return

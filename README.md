# ZorroHeater Project

This project provides a controller for a heater system based on the ESP32 platform on MicroPython. It uses MQTT for remote communication, allowing the user to set the desired temperature and receive sensor readings. The codebase should be pretty universal.

## :fire: Liability Disclaimer :fire:

**WARNING:** This code is provided "AS IS" without warranty of any kind. Use of this code in any form acknowledges your acceptance of these terms.

Always approach such systems with caution. Ensure you understand the code, the systems involved, and the potential risks. If you're unsure, **DO NOT** use the code.

Stay safe and think before you act.

## Simulator
You can mess around with this project in the [ESP32 simulator](https://wokwi.com/projects/379601065746814977)
Press play then mess with the switches and temp sensors
Toggle IS_SIMULATION False if you'd like and manually simulate startup of a diesel heater (hint, increase exhaust temp during startup between each step)
Note that the simulator code is now old, but it can still be useful and fun to play with

## Features:

- **A full standalone Wi-Fi AP with built in web portal**
- **Remote control via MQTT**:
  - Set target temperature
  - Start or stop the heater
  - Receive various readings
  - Set various parameters
- **Temperature-based control** of air and fuel to regulate heating output.
- **Safety shutdown** including an emergency stop thread and watchdogs.
- **Reconnect mechanisms** for WiFi and MQTT in case of disconnection.
- **Percentage and PID RPM Fan control** control the fan without RPM sensor, or be safer and use RPM based control with a hall effect sensor

## Hardware Requirements:

- ESP32 board
- Resistors, caps and such to build your board, NTC/PTC voltage divider
- MOSFETs for controlling air, fuel, glow plug, and water pump. Relay can work for glow plug as high current
- Single pole switch for manual start/stop

## Software Dependencies:

- imports are all based on the built-in MicroPython distribution. Shouldn't need additional imports.

## Setup:

1. Connect the ESP32/Raspberry Pi Pico/MicroPython compataible board and other hardware components according to the pin definitions in the code (will be basing hardware on Webastardo, eventually)
2. Replace `MYSSID` and `PASSWORD` in the code with your WiFi SSID and password.
3. Set the `MQTT_SERVER` variable to your MQTT broker's IP address (need to make this optional)
4. GO THROUGH THE CONFIG.py and UNDERSTAND and READ THE COMMENTS.
5. Flash the repo onto your ESP32.
6. Pray, and keep a fire entinguisher on hand.

## Usage:

- The system will automatically try to connect to the specified WiFi network and MQTT broker upon startup if configured.
- Use the MQTT topics `heater/set_temp` and `heater/command` to set the target temperature and send start/stop commands, respectively.
- The system will publish sensor readings to the `heater/sensor_values` topic at regular intervals.
- If the exhaust temperature exceeds the safety threshold, the system will automatically shut down, or at least it's supposed to.
- The switch can be used for manual start/stop control.

## Future Improvements/Ideas/Random notes:

- ~~Possibly implement a PID controller for more accurate temperature control.~~ Implemented a fan PID controller. Linear is good enough for overall temp
- Add support for more sensors and actuators, make things configurable. In progress.
- Improve error handling and system resilience.
- Possibly use an external ADC chip like the DS1232/ADS1234 to get around ESP32 ADC noise issues
- Would be nice to have some sort of air/fuel autotune
- Eventually would be nice to have a custom/own board that's universal use friendly, such as with screw wire terminals

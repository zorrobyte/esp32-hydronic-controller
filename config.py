import machine

# ┌─────────────────────┐
# │  General Settings   │
# └─────────────────────┘
USE_WIFI = False  # Use Wi-Fi (not functional yet)
USE_MQTT = False  # Use MQTT (not functional yet)
IS_WATER_HEATER = True  # True if controlling a Water/Coolant Heater
HAS_SECOND_PUMP = True  # True if driving a second water pump
IS_LILYGO_TRELAY_BOARD = True
IS_SIMULATION = True  # True to run in simulation mode

# ┌─────────────────────┐
# │  Safety Limits      │
# └─────────────────────┘
EXHAUST_SAFE_TEMP = 100  # Max safe temp for exhaust (°C)
OUTPUT_SAFE_TEMP = 90  # Max safe temp for output (°C)
EXHAUST_SHUTDOWN_TEMP = 40.0  # Exhaust shutdown temp (°C)

# ┌─────────────────────┐
# │  WiFi Settings      │
# └─────────────────────┘
SSID = "MYSSID"  # WiFi SSID
PASSWORD = "PASSWORD"  # WiFi Password

# ┌─────────────────────┐
# │  MQTT Settings      │
# └─────────────────────┘
MQTT_SERVER = "10.0.0.137"  # MQTT Server IP
MQTT_CLIENT_ID = "esp32_heater"  # MQTT Client ID
SET_TEMP_TOPIC = "heater/set_temp"  # Topic for setting temp
SENSOR_VALUES_TOPIC = "heater/sensor_values"  # Topic for sensor values
COMMAND_TOPIC = "heater/command"  # Topic for commands

# ┌─────────────────────┐
# │  Device Control     │
# └─────────────────────┘
TARGET_TEMP = 60.0  # Target temp (°C)
MIN_FAN_PERCENTAGE = 20  # Min fan speed (%)
MAX_FAN_PERCENTAGE = 100  # Max fan speed (%)
MIN_PUMP_FREQUENCY = 1  # Min pump freq (Hz)
MAX_PUMP_FREQUENCY = 5  # Max pump freq (Hz)
PUMP_ON_TIME = 0.02  # Pump on time per pulse (s)

# ┌─────────────────────┐
# │  Global Variables   │
# └─────────────────────┘
pump_frequency = 0  # Hz of the fuel pump, MUST be a global as it's ran in another thread
startup_attempts = 0  # Counter for failed startup attempts
startup_successful = True  # Flag to indicate if startup was successful
current_state = 'INIT'  # State the control is in

# ┌─────────────────────┐
# │  Pin Assignments    │
# └─────────────────────┘
# Helper class for inverted relay control (Lilygo T-Relay board)
if IS_LILYGO_TRELAY_BOARD:
    class InvertedRelay:
        def __init__(self, pin_number):
            self.pin = machine.Pin(pin_number, machine.Pin.OUT)
            self.on()  # Initialize to real world OFF state

        def on(self):
            self.pin.off()  # Inverted logic: OFF turns relay ON

        def off(self):
            self.pin.on()  # Inverted logic: ON turns relay OFF


    # Initialize the relay pins
    GLOW_PIN = InvertedRelay(22)  # Replace 22 with the GPIO pin you're using for the relay
    if IS_WATER_HEATER:
        WATER_PIN = InvertedRelay(23)
    if HAS_SECOND_PUMP:
        WATER_SECONDARY_PIN = InvertedRelay(21)
else:
    GLOW_PIN = machine.Pin(21, machine.Pin.OUT)
    if IS_WATER_HEATER:
        WATER_PIN = machine.Pin(19, machine.Pin.OUT)
    if HAS_SECOND_PUMP:
        WATER_SECONDARY_PIN = machine.Pin(20, machine.Pin.OUT)

# Pin Definitions
AIR_PIN = machine.Pin(23, machine.Pin.OUT)
FUEL_PIN = machine.Pin(22, machine.Pin.OUT)
SWITCH_PIN = machine.Pin(33, machine.Pin.IN, machine.Pin.PULL_UP)

# Initialize ADC for output and exhaust temperature
OUTPUT_TEMP_ADC = machine.ADC(machine.Pin(32))  # Changed to a valid ADC pin
OUTPUT_TEMP_ADC.atten(machine.ADC.ATTN_11DB)  # Corrected: Full range: 3.3v
EXHAUST_TEMP_ADC = machine.ADC(machine.Pin(34))  # Changed to a valid ADC pin
EXHAUST_TEMP_ADC.atten(machine.ADC.ATTN_11DB)  # Corrected: Full range: 3.3v

# Initialize PWM for air
air_pwm = machine.PWM(AIR_PIN)
air_pwm.freq(1000)
air_pwm.duty(0)  # Ensure the fan isn't initially on after init

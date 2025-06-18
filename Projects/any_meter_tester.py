from module import Module
from tester import Tester
from projectConfig import ProrjectConfig
from machine import Pin
from libs.climate import Climate
from libs.colorsensor import ColorSensor
from libs.distance import Distance
import time

project_config = ProrjectConfig(
    title="Any Meter",
    modules=[
        Module(Module.TOUCH_SENSOR, 'D'),
        Module(Module.MICROPHONE, 'C'),
        Module(Module.COLOR_SENSOR, 'B'),
        Module(Module.DISTANCE_SENSOR, 'E'),
        Module(Module.CLIMATE_SENSOR, "F")
    ],
    led_tower=True
)

Modes = [
    "Color Sensor",
    "Microphone",
    "Distance Sensor",
    "Climate Sensor"
]

###--- Climate Sensor Tester ---###
### If we want we can add humidity and pressure
temp_min = 20
temp_max = 30
color_temp_min = (255, 255, 0)
color_temp_max = (255, 0, 0)

def lerp_color(color1, color2, t):
    return tuple(int(color1[i] + (color2[i] - color1[i]) * t) for i in range(3))

def map_range(x, in_min, in_max, out_min, out_max):
    if x < in_min:
        return out_min
    if x > in_max:
        return out_max
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def show_value(np, value, min_val, max_val, color_start, color_end=None):
    length = map_range(value, min_val, max_val, 0, np.n)
    for i in range(np.n):
        if i < length:
            if color_end is not None:
                t = i / max(length - 1, 1)
                c = lerp_color(color_start, color_end, t)
            else:
                c = color_start
            np[i] = c
        else:
            np[i] = (0, 0, 0)
    np.write()

def climatesensor_mode(np, data, data_max=temp_max, data_min=temp_min, color_data_min=color_temp_min, color_data_max=color_temp_max):
    val = max(min(data, data_max), data_min)
    show_value(np, val, data_min, data_max, color_data_min, color_data_max)
###--- Climate Sensor Tester ---###


###--- Color Sensor Tester ---###
def colorsensor_mode(np, color, leds_num=8):
    r = min(int(color['red'] / 65535 * 255) * 3, 255)
    g = min(int(color['green'] / 65535 * 255) * 3, 255)
    b = min(int(color['blue'] / 65535 * 255) * 3, 255)
    for i in range(leds_num):
        np[i] = (r, g, b)
    np.write()
###--- Color Sensor Tester ---###


###--- Microphone Tester ---###
max_deviation = 0

def microphone_mode(np, mic_value, decay_rate=100, leds_num=8):
    global max_deviation
    deviation = abs(mic_value - 32768)
    if deviation > max_deviation:
        max_deviation = deviation
    else:
        max_deviation -= decay_rate
    
    max_deviation = max(max_deviation, 0)

    fill_value = int(max_deviation / 32768 * leds_num) + 1
    fill_value = min(fill_value, leds_num) 

    for i in range(fill_value):
        color = (0, 50, 0) if i < 5 else (50, 0, 0)
        if i == fill_value - 1:
            color = (50, 20, 0)
        np[i] = color
    for i in range(fill_value, 8):
        np[i] = (0, 0, 0)
    np.write()
###--- Microphone Tester ---###


###--- Distance Sensor Tester ---###
min_dist = 50
max_dist = 300

def get_color_by_distance(dist, min_dist=min_dist, max_dist=max_dist):
    if dist > max_dist:
        return (0, 255, 0)
    elif dist < min_dist:
        return (255, 0, 0) 
    else:
        ratio = (dist - min_dist) / (max_dist - min_dist)
        red = int(255 * (1 - ratio))
        green = int(255 * ratio)
        return (red, green, 0)
    
def display_bar(np, dist, leds_num=8, min_dist=min_dist, max_dist=max_dist):
    dist = max(min_dist, min(dist, max_dist))
    level = int((dist - min_dist) / (max_dist - min_dist) * leds_num)
    color = get_color_by_distance(dist)

    for i in range(leds_num):
        np[i] = color if i < level else (0, 0, 0)
    np.write()

def distance_mode(np, sensor, dist, leds_num=8):
    if sensor.is_valid(dist):
        display_bar(np, dist)
    else:
        for i in range(leds_num):
            np[i] = (0, 0, 0)
        np.write()
###--- Distance Sensor Tester ---###


class AnyMeterTester(Tester):
    def __init__(self):
        super().__init__(project_config)

    def init(self):
        super().init()
        for module in self.modules:
            if module.name == Module.MICROPHONE:
                self.microphone = module.getADC()
            if module.name == Module.TOUCH_SENSOR:
                self.touch = module.getPin(Pin.IN)
            if module.name == Module.DISTANCE_SENSOR:
                self.distance_sensor = Distance(module.getSlot(), soft=True)
            if module.name == Module.CLIMATE_SENSOR:
                self.climate_sensor = Climate(module.getSlot())
            if module.name == Module.COLOR_SENSOR:
               self.color_sensor = ColorSensor(module.getSlot(), soft=True)
        self.mode = 0
        self.last_touch = 0
        
    def loop(self):
        if self.touch.value() == 1 and (time.ticks_ms() - self.last_touch) > 500:
            self.mode = (self.mode + 1) % len(Modes)
            self.last_touch = time.ticks_ms()
            print(f"Mode changed to: {Modes[self.mode]}")

        # Color Sensor Tester
        if self.mode == 0:
            color = self.color_sensor.readRGB()
            colorsensor_mode(self.led_tower, color)

        # Microphone Tester
        if self.mode == 1:
            mic_value = self.microphone.read_u16()
            microphone_mode(self.led_tower, mic_value)

        # Distance Sensor Tester
        if self.mode == 2:
            distance = self.distance_sensor.read()
            distance_mode(self.led_tower, self.distance_sensor, distance)
        
        # Climate Sensor Tester
        if self.mode == 3:
            data = self.climate_sensor.read()
            climatesensor_mode(self.led_tower, data["temperature"])

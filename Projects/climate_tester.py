from machine import Pin
import time
from libs.climate import Climate  # твой класс для датчика
from tester import Tester
from projectConfig import ProrjectConfig
from module import Module
from neopixel import NeoPixel

project_config = ProrjectConfig(
    title="Climate Tester",
    modules=[
        Module(Module.CLIMATE_SENSOR, "A"),
        Module(Module.TOUCH_SENSOR, "B")
    ],
    led_tower=True
)
temp_min = 15
temp_max = 30
color_temp_min = (255, 255, 0)   # желтый
color_temp_max = (255, 0, 0)     # красный

hum_min = 0
hum_max = 100
color_hum_min = (173, 216, 230)  # нежно голубой
color_hum_max = (0, 0, 255)      # синий

pres_min = 900
pres_max = 1050
color_pres = (255, 255, 255)

mode = 0
last_touch = 0

def map_range(x, in_min, in_max, out_min, out_max):
    if x < in_min:
        return out_min
    if x > in_max:
        return out_max
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def lerp_color(color1, color2, t):
    return tuple(int(color1[i] + (color2[i] - color1[i]) * t) for i in range(3))


def show_value(np : NeoPixel, value, min_val, max_val, color_start, color_end=None):
    # при минимуме 0 светодиодов, при максимуме все
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
    print(length)

class ClimateTester(Tester):
    def __init__(self):
        super().__init__(project_config)

    def init(self):
        super().init()
        for module in self.modules:
            if module.name == Module.TOUCH_SENSOR:
                self.touch = module.getPin(Pin.IN)
            if module.name == Module.CLIMATE_SENSOR:
                self.climate = Climate(module.getSlot())

    
    def loop(self):
        global last_touch, mode
        if self.touch.value() == 1 and (time.ticks_ms() - last_touch) > 500:
            mode = (mode + 1) % 3
            last_touch = time.ticks_ms()

        data = self.climate.read()
        temp = data["temperature"]
        hum = data["humidity"]
        pres = data["pressure"]

        if mode == 0:
            val = max(min(temp, temp_max), temp_min)
            show_value(self.led_tower, val, temp_min, temp_max, color_temp_min, color_temp_max)
            print(f"Температура: {temp:.2f} °C")

        elif mode == 1:
            val = max(min(hum, hum_max), hum_min)
            show_value(self.led_tower, val, hum_min, hum_max, color_hum_min, color_hum_max)
            print(f"Влажность: {hum:.2f} %")

        else:
            val = max(min(pres, pres_max), pres_min)
            show_value(self.led_tower, val, pres_min, pres_max, color_pres)
            print(f"Давление: {pres:.2f} гПа")

        time.sleep(0.2)

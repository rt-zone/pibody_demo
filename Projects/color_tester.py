from machine import Pin
from libs.colorsensor import ColorSensor
from tester import Tester
from projectConfig import ProrjectConfig
from module import Module
import time

project_config = ProrjectConfig(
    title="Color Tester",
    modules=[
        Module(Module.LED_R, "A"),
        Module(Module.LED_Y, "B"),
        Module(Module.LED_G, "C"),
        Module(Module.COLOR_SENSOR, "D"),
    ]
)
def led_change(leds, led_index):
    for i in range(len(leds)):
        if i == led_index:
            leds[i].on()
        else:
            leds[i].off()

class ColorTester(Tester):
    def __init__(self):
        super().__init__(project_config)

    def init(self):
        super().init()
        for module in self.modules:
            if module.name == Module.LED_R:
                self.led_r = module.getPin(Pin.OUT)
            if module.name == Module.LED_Y:
                self.led_y = module.getPin(Pin.OUT)
            if module.name == Module.LED_G:
                self.led_g = module.getPin(Pin.OUT)
            if module.name == Module.COLOR_SENSOR:
                self.color_sensor = ColorSensor(module.getSlot())   
        self.leds = [self.led_r, self.led_y, self.led_g]

    def loop(self):
        color = self.color_sensor.detectColor()

        if color == "orange":
            led_change(self.leds, 0)
        elif color == "yellow":
            led_change(self.leds, 1)
        elif color == "green":
            led_change(self.leds, 2)
        else:
            led_change(self.leds, -1)

        time.sleep(0.1)  # Задержка для предотвращения слишком частого опроса сенсора

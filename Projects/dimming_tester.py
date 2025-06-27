from machine import Pin
import time
from tester import Tester
from projectConfig import ProjectConfig
from module import Module

project_config = ProjectConfig(
    title="Dimming System",
    modules=[
        Module(Module.LED_R, "A"),
        Module(Module.MOTION_DETECTOR, "B"),
        Module(Module.LIGHT_SENSOR, "C")
    ]
)

light_treshold = 37500  # максимальное значение для светодиода
dim_brightness = 2500   # начальная яркость светодиода
full_brightness = 35000 # максимальная яркость светодиода

def fade_to(brightness, led, step=1000, delay=0.02):
    current = led.duty_u16()
    if brightness > current:
        for i in range(current, brightness, step):
            led.duty_u16(i)
            time.sleep(delay)
    else:
        for i in range(current, brightness, -step):
            led.duty_u16(i)
            time.sleep(delay)
    led.duty_u16(brightness)

class DimmingTester(Tester):
    def __init__(self):
        super().__init__(project_config)

    def init(self):
        super().init()
        for module in self.modules:
            if module.name == Module.LED_R:
                self.led = module.getPWM()
                self.led.freq(1000)
            if module.name == Module.MOTION_DETECTOR:
                self.motion = module.getPin(Pin.IN)
            if module.name == Module.LIGHT_SENSOR:
                self.light = module.getADC()

    def loop(self):
        light_value = self.light.read_u16()
        motion_value = self.motion.value()

        if light_value > light_treshold:
            fade_to(0, self.led)
            return
        if motion_value == 1:
            fade_to(full_brightness, self.led)
            time.sleep(2.5) 
        else:
            fade_to(dim_brightness, self.led)

    time.sleep(0.2)

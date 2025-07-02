from machine import Pin
import time
from Tester.hinter import Hinter
from Tester.tester import Tester
from Tester.projectConfig import ProjectConfig
from Tester.module import Module

hinter = Hinter()

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

x = 10
y = 32
length = 200
height = 9
border = True

def fade_to(brightness, led, step=1000, delay=0.01):
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
        self.color = hinter.display.color(0, 0, 0)

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

        hinter.display.text("Light Sensor is working   ", x, y - 22)
        hinter.display.text("Light value: " + str(65535 - light_value) + "/28035          ", x, y + 9)
        hinter.display.linear_bar(x, y, length, value=65535 - light_value, min_value=0, max_value=65535, height=height, border=True, color=self.color)

        if light_value > light_treshold:
            self.color = hinter.display.color(64, 64, 64)
            fade_to(0, self.led)
            return
        if motion_value == 1:
            self.color = hinter.display.color(255, 255, 0)
            fade_to(full_brightness, self.led)
        else:
            self.color = hinter.display.color(88, 88, 0)
            fade_to(dim_brightness, self.led)

        if not self.isRunning:
            hinter.drawModules(project_config)
            return

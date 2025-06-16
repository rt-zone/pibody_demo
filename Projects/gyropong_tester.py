from machine import Pin
from libs.gyroaxel import GyroAxel
from tester import Tester
from module import Module
from projectConfig import ProrjectConfig
import time

project_config = ProrjectConfig(
    title = "GyroPong",
    modules=[
        Module(Module.LED_R, "A"),
        Module(Module.LED_Y, "B"),
        Module(Module.LED_G, "C"),
        Module(Module.BUZZER, "D"),
        Module(Module.GYRO, "E")
    ]
)

treshold = 0.5 
led_index = 0
last_index = 0
last_time = 0
freq_map = {
    0: 440,  # A4  
    1: 330,  # E4
    2: 220,  # C4
} 

def beep(buzzer, freq, duration=0.05):
    buzzer.freq(freq)
    buzzer.duty_u16(4096)
    time.sleep(duration)
    buzzer.duty_u16(0)

def change_index(index, change):
    index += change
    index = min(max(index, 0), len(freq_map) - 1)
    return index

def update_leds(leds, index):
    for i in range(len(leds)):
        if i == index:
            leds[i].on()
        else:
            leds[i].off()

class GyroPongTester(Tester):
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
            if module.name == Module.BUZZER:
                self.buzzer = module.getPWM()
                self.buzzer.freq(440)
            if module.name == Module.GYRO:
                self.gyro = GyroAxel(module.getSlot())
        self.leds = [self.led_r, self.led_y, self.led_g]

    def loop(self):
        global led_index, last_time, last_index
        x, y, z = self.gyro.read_accel_data()

        if x > treshold:
            if (time.ticks_diff(time.ticks_ms(), last_time) > 250):
                led_index = change_index(led_index, -1)
                last_time = time.ticks_ms()
                if last_index != led_index:
                    beep(self.buzzer, freq_map[led_index])
                    last_index = led_index

        elif x < -treshold:
            if (time.ticks_diff(time.ticks_ms(), last_time) > 250):
                led_index = change_index(led_index, 1)
                last_time = time.ticks_ms()
                if last_index != led_index:
                    beep(self.buzzer, freq_map[led_index])
                    last_index = led_index

        update_leds(self.leds, led_index)
        time.sleep(0.1)

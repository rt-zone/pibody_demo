from projectConfig import ProrjectConfig
from neopixel import NeoPixel
from machine import PWM, Pin, ADC
from module import Module

cancel_button = Pin(20, Pin.IN)
isRunning = True

def cancel_handler(pin):
    global isRunning
    isRunning = False
    print("Test cancelled")

cancel_button.irq(trigger=Pin.IRQ_FALLING, handler=cancel_handler) 

class Tester():
    def __init__(self, project_config: ProrjectConfig):
        self.config = project_config
        self.name = project_config.getTitle()

    def loop(self):
        pass

    def init(self):
        project_config = self.config
        self.name = project_config.getTitle()

        config = self.config
        self.modules = config.getModules()

        if config.getLedTower():
            self.led_tower = NeoPixel(Pin(8), 8)

        if config.getServo8():
            self.servo = PWM(Pin(8))

        if config.getServo9():
            self.servo9 = PWM(Pin(9))  

    def start(self):
        self.init()
        while isRunning:
            self.loop()
from machine import Pin, ADC
from time import sleep, ticks_ms
from module import Module 
from projectConfig import ProrjectConfig
from tester import Tester

project_config = ProrjectConfig(
    title="RGB Tester",
    modules=[
        Module(Module.BUTTON_BLUE, "A"),
        Module(Module.BUTTON_YELLOW, "B"),
        Module(Module.POTENTIOMETER, "C"),
        Module(Module.TOUCH_SENSOR, "D"),
        Module(Module.SWITCH, "F")
    ],
    led_tower=True,
)
class ModeManager:
    def __init__(self, np, adc, n=8):
        self.np = np
        self.adc = adc
        self.n = n
        self.current_mode = 0
        self.current_color = (102, 0, 0)  # Красный
        self.colors = [
            (102, 0, 0), (0, 102, 0), (0, 0, 102),
            (102, 102, 0), (0, 102, 102), (102, 0, 102),
            (102, 102, 102), (102, 66, 0)
        ]
        self.rainbow_offset = 0
        self.comet_direction = 1
        self.last_update = 0
        self.brightness = 0.4

        self.modes = [
            ("Сплошной цвет", self.mode_solid),
            ("Радуга", self.mode_rainbow),
            ("Комета", self.mode_comet),
            ("Мерцание", self.mode_blink)
        ]

    def apply_brightness(self, color):
        return tuple(int(c * self.brightness) for c in color)

    def get_speed(self):
        pot_value = self.adc.read_u16()
        if self.current_mode == 1:  # Радуга
            return 50 - int((pot_value / 65535) * 49)
        return 200 - int((pot_value / 65535) * 150)

    def mode_off(self):
        for i in range(self.n):
            self.np[i] = (0, 0, 0)
        self.np.write()

    def mode_solid(self):
        color = self.apply_brightness(self.current_color)
        for i in range(self.n):
            self.np[i] = color
        self.np.write()

    def mode_rainbow(self):
        for i in range(self.n):
            pos = ((i * 256 // self.n) + self.rainbow_offset) % 256
            if pos < 85:
                r, g, b = pos * 3, 255 - pos * 3, 0
            elif pos < 170:
                pos -= 85
                r, g, b = 255 - pos * 3, 0, pos * 3
            else:
                pos -= 170
                r, g, b = 0, pos * 3, 255 - pos * 3
            self.np[i] = self.apply_brightness((r, g, b))
        self.np.write()
        self.rainbow_offset = (self.rainbow_offset + 1) % 256

    def mode_comet(self):
        color = self.apply_brightness(self.current_color)
        tail = 2
        speed = self.get_speed()
        tick = (ticks_ms() // speed) % (self.n * 2 - 2)

        head = tick if tick < self.n else (self.n * 2 - 2) - tick
        self.comet_direction = 1 if tick < self.n else -1

        for i in range(self.n):
            self.np[i] = (0, 0, 0)

        for i in range(tail + 1):
            pos = head - i * self.comet_direction
            if 0 <= pos < self.n:
                fade = 1.0 if i == 0 else (tail - i + 1) / (tail + 1)
                self.np[pos] = tuple(int(c * fade) for c in color)

        self.np.write()

    def mode_blink(self):
        color = self.apply_brightness(self.current_color)
        blink_state = (ticks_ms() // (self.get_speed() * 5)) % 2
        for i in range(self.n):
            self.np[i] = color if blink_state else (0, 0, 0)
        self.np.write()

    def run_current_mode(self):
        self.modes[self.current_mode][1]()


class NeoPixelTester(Tester):
    def __init__(self):
        super().__init__(project_config)
    def init(self):
        super().init()
        for module in self.modules:
            if module.name == Module.BUTTON_BLUE:
                self.btn_prev = module.getPin(Pin.IN)
            if module.name == Module.BUTTON_YELLOW:
                self.btn_next = module.getPin(Pin.IN)
            if module.name == Module.POTENTIOMETER:
                self.adc = module.getADC()
            if module.name == Module.TOUCH_SENSOR:
                self.btn_color = module.getPin(Pin.IN)
            if module.name == Module.SWITCH:
                self.switch = module.getPin(Pin.IN)
        self.np = self.led_tower
        self.manager = ModeManager(self.np, self.adc, 8)

        self.last_button_press = 0
        self.debounce = 200

    def debounce_check(self):
        return ticks_ms() - self.last_button_press > self.debounce

    def handle_buttons(self):
        if not self.debounce_check():
            return

        if self.btn_prev.value() == 1:
            self.manager.current_mode = (self.manager.current_mode - 1) % len(self.manager.modes)
            print("Режим:", self.manager.modes[self.manager.current_mode][0])
            self.last_button_press = ticks_ms()
            while self.btn_prev.value() == 1: sleep(0.001)

        if self.btn_next.value() == 1:
            self.manager.current_mode = (self.manager.current_mode + 1) % len(self.manager.modes)
            print("Режим:", self.manager.modes[self.manager.current_mode][0])
            self.last_button_press = ticks_ms()
            while self.btn_next.value() == 1: sleep(0.001)

        if self.btn_color.value() == 1:
            idx = self.manager.colors.index(self.manager.current_color)
            self.manager.current_color = self.manager.colors[(idx + 1) % len(self.manager.colors)]
            print("Цвет изменен на:", self.manager.current_color)
            self.last_button_press = ticks_ms()
            while self.btn_color.value() == 1: sleep(0.001)

    def loop(self):
        self.handle_buttons()
        if self.switch.value() == 0:
            self.manager.mode_off()
            sleep(0.1)
            return
        self.manager.run_current_mode()
        sleep(0.005)


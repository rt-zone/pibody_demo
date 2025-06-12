import vga2_bold_16x32 as font
import vga2_8x16 as font_small
import st7789
from module import Module
from projectConfig import ProrjectConfig

SLOTS_COORDS = {
    "A": (10, 0),
    "B": (10, 90),
    "C": (10, 180),
    "D": (150, 0),
    "E": (150, 90),
    "F": (150, 180)
}
    
class Hinter():
    def __init__(self, tft: st7789.ST7789):
        self.tft = tft
        self.clear()

    def clear(self):
        self.tft.fill(st7789.BLACK)

    def drawModule(self, module :Module, slot):
        x, y = SLOTS_COORDS[slot]
        self.tft.rect(x, y, 110, 110, st7789.BLACK)
        self.tft.png(module.getPngPath(), x, y)

    def drawModules(self, config: ProrjectConfig):
        title = config.getTitle()
        led_tower = config.getLedTower()
        servo8 = config.getServo8()
        servo9 = config.getServo9()
        modules = config.getModules()

        self.tft.fill(st7789.BLACK)  # Clear the screen
        for module in modules:
            slot = module.getSlot()

            if slot in SLOTS_COORDS:
                self.drawModule(module, slot)
            else:
                print(f"Invalid slot: {slot}")

        self.tft.text(font, title, 10, 280, st7789.WHITE, st7789.BLACK)
        if led_tower:
            self.tft.png("module_pngs/led_tower.png", 110, 0)
        if servo8 or servo9:
            self.tft.png("module_pngs/servo.png", 90, 200)
            txt = "8" if servo8 else ""
            txt += "/" if servo8 and servo9 else ""
            txt += "9" if servo9 else ""
            self.tft.text(font_small, txt, 110, 250, st7789.WHITE, st7789.BLACK)

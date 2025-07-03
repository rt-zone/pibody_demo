from pibody import Display
from Tester.module import Module
from Tester.projectConfig import ProjectConfig

SLOTS_COORDS = {
    "A": (10, 0),
    "B": (10, 90),
    "C": (10, 180),
    "D": (150, 0),
    "E": (150, 90),
    "F": (150, 180)
}
    
class Hinter():
    def __init__(self):
        self.display = Display()
        self.clear()

    def tester_is_running(self, tester_name):
        self.clear()
        text_color = self.display.color(120, 255, 50)  # Green color
        self.display.text(f"{tester_name}", 10, 120, self.display.font_bold, text_color, self.display.BLACK)
        self.display.text("is running", 10, 150, self.display.font_bold, text_color, self.display.BLACK)
        self.display.text("GP21", 204, 300, self.display.font_small, fg=self.display.CYAN)
        self.display.text("cancel", 154, 300, self.display.font_small)

    def clear(self):
        self.display.fill(self.display.BLACK)

    def drawModule(self, module :Module, slot):
        x, y = SLOTS_COORDS[slot]
        self.display.rect(x, y, 110, 110, self.display.BLACK)
        self.display.png(module.getPngPath(), x, y)

    def drawModules(self, config: ProjectConfig):
        title = config.getTitle()
        led_tower = config.getLedTower()
        servo8 = config.getServo8()
        servo9 = config.getServo9()
        modules = config.getModules()


        self.display.fill(self.display.BLACK)  # Clear the screen
        for module in modules:
            slot = module.getSlot()

            if slot in SLOTS_COORDS:
                self.drawModule(module, slot)
            else:
                print(f"Invalid slot: {slot}")

        self.display.text(title, 10, 265, self.display.font_bold, self.display.WHITE, self.display.BLACK)
        self.display.text("GP20", 10, 300, self.display.font_small, fg=self.display.CYAN)
        self.display.text("select", 44, 300, self.display.font_small)
        self.display.text("GP21", 204, 300, self.display.font_small, fg=self.display.CYAN)
        self.display.text("next", 170, 300, self.display.font_small)
        if led_tower:
            self.display.png("module_pngs/led_tower.png", 110, 0)
        if servo8 or servo9:
            self.display.png("module_pngs/servo.png", 90, 200)
            txt = "8" if servo8 else ""
            txt += "/" if servo8 and servo9 else ""
            txt += "9" if servo9 else ""
            self.display.text(font=self.display.font_small, text=txt, x=110, y=250, fg=self.display.WHITE, bg=self.display.BLACK)

    def show_error(self, message):
        self.clear()
        text_color = self.display.color(120, 100, 20)
        
        lines = [message[i:i+28] for i in range(0, len(message), 28)]
        for i, line in enumerate(lines):
            self.display.text(font=self.display.font_small, text=line, x=10, y=20 + i * 20, fg=text_color, bg=self.display.BLACK)
        self.display.text("GP20", 10, 300, self.display.font_small, fg=self.display.CYAN)
        self.display.text("select", 44, 300, self.display.font_small)
        self.display.text("GP21", 204, 300, self.display.font_small, fg=self.display.CYAN)
        self.display.text("next", 170, 300, self.display.font_small)
        

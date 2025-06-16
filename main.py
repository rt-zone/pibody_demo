from tft_config import config
from hinter import Hinter
from Projects.climate_tester import ClimateTester
from Projects.rgb_tester import NeoPixelTester
from Projects.dimming_tester import DimmingTester
from Projects.gyropong_tester import GyroPongTester
from tester import Tester
from machine import Pin
start_button = Pin(20, Pin.IN) 
select_button = Pin(21, Pin.IN)

tft = config()
tft.init()
hinter = Hinter(tft)

testers = [
    GyroPongTester(),
    ClimateTester(),
    NeoPixelTester(),
    DimmingTester()
]

selected_tester = testers[0]  # Default to the first tester
tester_index = 0
def select_tester(tester: Tester):
    global selected_tester
    hinter.clear()
    if selected_tester is not None:
        selected_tester.stop()
    selected_tester = tester

    hinter.drawModules(selected_tester.config)

def cancel_handler(pin):
    selected_tester.cancel_handler(pin)
    hinter.drawModules(selected_tester.config)
    pin.irq(handler=None)  # Disable the cancel handler

def start_selected_tester():
    if selected_tester is not None:
        hinter.tester_is_running(selected_tester.name)
        select_button.irq(trigger=Pin.IRQ_RISING, handler=cancel_handler) 
        selected_tester.start()
    else:
        print("No tester selected")


select_tester(selected_tester)  # Initialize with the first tester


while True:
    if select_button.value() == 1:
        tester_index = (tester_index + 1) % len(testers)
        select_tester(testers[tester_index])
        while select_button.value() == 1: pass
    if start_button.value() == 1:
        try:
            start_selected_tester()
        except Exception as e:
            print(f"Error starting tester: {e}")
            hinter.show_error(str(e))
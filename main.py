from tft_config import config
from hinter import Hinter
from Projects.climate_tester import ClimateTester
from Projects.rgb_tester import NeoPixelTester

tft = config()
tft.init()
hinter = Hinter(tft)



# tester = ClimateTester()
# hinter.drawModules(tester.config)
# tester.start()
    
tester = NeoPixelTester()
hinter.drawModules(tester.config)
tester.start()


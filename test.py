# TODO: delete file
from PlcCLient import PlcClient
import time

plc = PlcClient()
plc.initButtons()

# plc.login('PLC')

time.sleep(3)
plc.openDoorsButton.toggleButton()

plc.close()
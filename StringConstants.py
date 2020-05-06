# Server configuration variables
SERVER_IP_ADDRESS = "192.168.0.102"
VIDEO_COMMAND_PORT = 8000
IMAGE_PORT = 8001

# Messages: These messages are the ones that are used to command the actions of the Nest
MESSAGE_SYSTEM_POWER = "systemPower"
MESSAGE_EMERGENCY_STOP = "emergencyStop"
MESSAGE_OPEN_DOORS = "openDoors"
MESSAGE_CLOSE_DOORS = "closeDoors"
MESSAGE_OPEN_ROOF = "openRoof"
MESSAGE_CLOSE_ROOF = "closeRoof"
MESSAGE_EXTEND_PAD = "extendPad"
MESSAGE_RETRACT_PAD = "retractPad"
MESSAGE_RAISE_PAD = "raisePad"
MESSAGE_LOWER_PAD = "lowerPad"
MESSAGE_SYSTEM_STATUS = "systemStatus"
MESSAGE_BOTTOM_DRONE_MISSION = "bottomDroneMission"
MESSAGE_TOP_DRONE_MISSION = "topDroneMission"
MESSAGE_CONNECTION_TEST = "Connection Test"

# Error messages: The error prefix is relevant because it is how the clients know when an error has occured.count
#                 They parse the error prefix to get error messages. The error dictionary represents different states
#                 that can occur within the nest. 
ERROR_PREFIX = "Error: "

ERROR_UNKNOWN_MESSAGE = "Unknown Message"
ERROR_IS_ON = "Must turn system off"
ERROR_IS_OFF = "Must turn system on"
ERROR_DOORS_ARE_OPEN = "Must close doors"
ERROR_DOORS_ARE_CLOSED = "Must open doors"
ERROR_ROOF_IS_OPEN = "Must close roof"
ERROR_ROOF_IS_CLOSED = "Must open roof"
ERROR_PAD_IS_EXTENDED = "Must retract pad"
ERROR_PAD_IS_RETRACTED = "Must extend pad"
ERROR_PAD_IS_RAISED = "Must lower pad"
ERROR_PAD_IS_LOWERED = "Must raise pad"
ERROR_IS_STARTED = "Must stop system"

# PLC Client 
# Location of chromedriver which can be downloaded from https://sites.google.com/a/chromium.org/chromedriver/ 
# download this and copy and paste where that file is here vvvv
# CHROMEDRIVERLOCATION = "C:\\Users\ECE436_18\Desktop\Scripts\chromedriver"
CHROMEDRIVERLOCATION = '/Users/laure/chromedriver'
PLCURL = 'http://192.168.99.3/'
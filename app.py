"""
Devils Invent: Nkk Switches Project (v1.1.0)
"""

import serial
import time
from builtins import bytes

# Config constants
BAUD_RATE = 115200

# Nkk Device command mappings
CMD_RESET = "24"
CMD_INC_1 = "2E33"
CMD_INC_2 = "2E34"
CMD_DEC_1 = "2E35"
CMD_DEC_2 = "2E36"
CMD_READY = "01"
CMD_ADD_TEXT_1 = "2751"
CMD_SELECT_IMG_1 = "2E31"
CMD_SELECT_IMG_2 = "2E32"

# Nkk device memory location mappings
MEM_LOC_1 = "30303031"
MEM_LOC_2 = "30303032"
MEM_LOC_EMPTY = "30303033" # There is no 3rd image

# Nkk event return-codes
EVT_PRESS_1 = b'\x81'
EVT_PRESS_2 = b'\x82'
EVT_RELEASE_1 = b'\xB1'
EVT_RELEASE_2 = b'\xB2'

# Device ready return-code
VAL_READY = 'a'

# Variables to keep track of what image is being displayed on each switch
_switch1_ndx = 1
_switch2_ndx = 1

# Serial COM object for serial connection to Nkk switch
ser = serial.Serial(
    port="COM6",
    baudrate=BAUD_RATE
)

def _initialize() -> None:
    """
    Resets the Nkk Switches

    Also sets images of each switch to their initial states.

        @returns None
    """

    reset()
    set_image(2, 1)
    set_image(1, 3)

def _request_ready() -> None:
    """
    Command Nkk switch to send "Ready" response.

        @return None
    """

    ser.write(bytes.fromhex(CMD_READY))

def increment_switch2() -> None:
    """
    Increments the image on switch 2 to the next image in storage.

    If the image is the last in storage, loops back and iterates from image 1 again.

        @returns None
    """

    global _switch2_ndx

    _switch2_ndx += 1
    if (_switch2_ndx > 2): _switch2_ndx = 1
    set_image(2, _switch2_ndx)


def set_image(btn:int, img:int) -> None:
    """
    Sets an image for a specified button.

        @arg btn:int The index of the button to set the image of.
        @arg img:int The index of the image to set on the button.
        @returns None
    """
    if (btn == 1):
        if (img == 1):
            ser.write(bytes.fromhex(CMD_SELECT_IMG_1 + MEM_LOC_1))
        elif(img == 2):
            ser.write(bytes.fromhex(CMD_SELECT_IMG_1 + MEM_LOC_2))
        elif(img == 3):
            ser.write(bytes.fromhex(CMD_SELECT_IMG_1 + MEM_LOC_EMPTY))
        
        _switch1_ndx = img
    elif (btn == 2):
        if (img == 1):
            ser.write(bytes.fromhex(CMD_SELECT_IMG_2 + MEM_LOC_1))
        elif(img == 2):
            ser.write(bytes.fromhex(CMD_SELECT_IMG_2 + MEM_LOC_2))
        
        _switch2_ndx == img

def reset() -> None:
    """
    Sends the reset command to the NKK Switches.

    Note: there is a half a second wait after the reset to ensure the switches have rebooted in time.

        @returns None
    """

    ser.write(bytes.fromhex(CMD_RESET))
    time.sleep(.5)

def print_text(text:str, btn:int = 1) -> None:
    """
    Prints teh specified text to the specified button.

    The NKK switches support data in teh following format over the IO stream: 0x27 0x51 (2 hex bytes) 
    0xAA 0xBB (2 ASCII hex bytes for number of characters to be sent) 0xCC 0xDD (2 ASCII hex bytes 
    for starting row) 0xEE 0xFF (2 ASCII hex bytes for starting column) 0xGG (2 ASCII hex bytes per 
    character to send)

        @arg text:str The text to display
        @arg btn:int The index of the button to display the text on.
        @returns None
    """
    msg = ""
    car_cnt = str(len(text))
    car_cnt = car_cnt if len(car_cnt) > 1 else "0" + car_cnt
    start_row = "17"
    start_col = "17"

    msg = CMD_ADD_TEXT_1 \
    + (bytes(car_cnt[0], "ascii").hex() + bytes(car_cnt[1], "ascii").hex()) \
    + (bytes(start_row[0], "ascii").hex() + bytes(start_row[1], "ascii").hex()) \
    + (bytes(start_col[0], "ascii").hex() + bytes(start_col[1], "ascii").hex())

    for c in text:
        val = bytes(c, "ascii").hex()
        msg += (bytes(val[0], "ascii").hex() + bytes(val[1], "ascii").hex())
    
    msg = msg.replace("b'", "").replace("'", "")

    print(f"Writing the following message to the screen: {text}. Bytes: {msg}")
    ser.write(bytes.fromhex(msg))

def print_user_input() -> None:
    """
    Prints details about user inputs from the NKK switches to the console of the 
    currently executing machine.

        @returns None
    """

    print('A table would like water.' if _switch2_ndx == 2 else 'A table is dissatisfied with the burger.')

def _handle_next_event() -> None:
    """
    Handles user input signals from the Nkk switches.

        @returns None
    """

    resp = ser.read()

    if (resp == EVT_PRESS_1):
        print_user_input()
    elif (resp == EVT_PRESS_2):
        increment_switch2()


def main() -> None:
    """
    The main point of execution for this application.

    This function initializes the Nkk Switches and the conneciton to them, then loops infinately to
    handle data that comes accross the communication stream.

        @returns None
    """

    ready = False

    while(not ready):
        _request_ready()
        ready = (ser.read() == b'a' and ser.isOpen())

    _initialize()
    print("Device ready.")
    
    # Print select on button 1
    print_text("Select")

    while(True):
        _handle_next_event()


# Runs the program.
main()
from adafruit_magtag.magtag import MagTag
from adafruit_led_animation.color import (
    RED,
    GREEN,
    BLUE,
    CYAN,
    WHITE,
    OLD_LACE,
    PURPLE,
    MAGENTA,
    YELLOW,
    ORANGE,
    PINK,
)
import time
import alarm
import board

# Get secrets from private file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# Get our username, key and desired timezone
aio_username = secrets["aio_username"]
aio_key = secrets["aio_key"]
location = secrets.get("timezone", None)

TIME_URL = (
    "https://io.adafruit.com/api/v2/%s/integrations/time/strftime?x-aio-key=%s"
    % (aio_username, aio_key)
)
TIME_URL += "&fmt=%25l:%25M %25p"

### --- GLOBAL VARIABLES --- ###
passActive = False
resetList = [False, False, False, False]
pixelColors = [RED, YELLOW, GREEN, BLUE]
flashTime = 0.1

magtag = MagTag(url=TIME_URL, rotation=180)
magtag_pixels = magtag.peripherals.neopixels
magtag_pixels.brightness = 1.0

### --- CUSTOM FUNCTIONS --- ###

# Custom flash sequence
def flashNeo(color):
    global magtag
    global magtag_pixels
    magtag.peripherals.neopixel_disable = False

    for i in range(3):
        magtag_pixels.fill(color)
        time.sleep(flashTime)
        magtag_pixels.fill((0, 0, 0))
        time.sleep(flashTime)
    magtag.peripherals.neopixel_disable = True


# Reset MagTag text for next Hall Pass use
def resetDisplay():
    global magtag
    global passActive
    magtag.set_text("Null", index=0, auto_refresh=False)
    magtag.set_text("Pass", index=1, auto_refresh=False)
    passActive = False
    magtag.refresh()


# Initialize display
def setupDisplay():
    global magtag

    magtag.graphics.set_background("/background.bmp")

    magtag.add_text(
        text_scale=3,
        text_position=((magtag.graphics.display.width // 2), 220),
        text_anchor_point=(0.5, 0.5),
    )
    magtag.add_text(
        text_scale=3,
        text_position=((magtag.graphics.display.width // 2), 250),
        text_anchor_point=(0.5, 0.5),
    )
    resetDisplay()


# Get current time and activate Hall Pass
def activateHallPass():
    global magtag
    global passActive
    try:
        currentTime = magtag.fetch(auto_refresh=False)
        currentTime = currentTime.strip().split(" ")
        flashNeo(GREEN)
        for i in range(len(currentTime)):
            magtag.set_text(currentTime[i], index=i, auto_refresh=False)
        passActive = True
        magtag.refresh()
    except (RuntimeError, ValueError) as e:
        print("Retrying - ", e)

def buttonChecker():
    global magtag
    global magtag_pixels

    while True:
        # Loop through buttons, checking for input
        if magtag.peripherals.any_button_pressed:
            # Try to connect to WiFi and activate the Hall Pass
            if passActive:
                magtag.peripherals.neopixel_disable = False
                if all(resetList):
                    magtag.peripherals.neopixel_disable = True
                    flashNeo(ORANGE)
                    resetDisplay()
                    magtag.peripherals.deinit()
                    return
                else:
                    if magtag.peripherals.button_a_pressed:
                        magtag_pixels[3] = pixelColors[3]
                        resetList[3] = True
                    elif magtag.peripherals.button_b_pressed:
                        magtag_pixels[2] = pixelColors[2]
                        resetList[2] = True
                    elif magtag.peripherals.button_c_pressed:
                        magtag_pixels[1] = pixelColors[1]
                        resetList[1] = True
                    elif magtag.peripherals.button_d_pressed:
                        magtag_pixels[0] = pixelColors[0]
                        resetList[0] = True
            else:
                try:
                    magtag.network.connect()
                    print("WiFi Success")
                    activateHallPass()
                except ConnectionError as e:
                    print("Retrying - ", e)
                    flashNeo(RED)

### --- RUNTIME CODE --- ###
setupDisplay()
buttonChecker()
pinAlarm = [
    alarm.pin.PinAlarm(pin=board.BUTTON_C, value=False, pull=True),
    alarm.pin.PinAlarm(pin=board.BUTTON_D, value=False, pull=True)
]
alarm.exit_and_deep_sleep_until_alarms(*pinAlarm)

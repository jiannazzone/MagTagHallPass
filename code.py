from adafruit_magtag.magtag import MagTag
import time
import alarm
import board
import random

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
flashTime = 0.1
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
pixelColors = [RED, YELLOW, GREEN, BLUE]

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

# Initialize display
def setupDisplay():
    global magtag
    global passActive
    global firstLaunch

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
    magtag.set_text('', index=0, auto_refresh=False)
    magtag.set_text('<- GO', index=1, auto_refresh=False)
    passActive = False
    magtag.refresh()


# Get current time and activate Hall Pass
def activateHallPass():
    global magtag
    global passActive

    try:
        magtag.network.connect()
        flashNeo(GREEN)
        print("WiFi Success")
    except ConnectionError as e:
        print("Retrying - ", e)
        flashNeo(RED)
        activateHallPass()

    try:
        currentTime = magtag.fetch(auto_refresh=False)
        currentTime = currentTime.strip().split(" ")
        for i in range(len(currentTime)):
            magtag.set_text(currentTime[i], index=i, auto_refresh=False)
        passActive = True
        magtag.refresh()
        print('Hall Pass Created')
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
                    flashNeo(RED)
                    magtag.peripherals.deinit()
                    setupDisplay()
                    return
                else:
                    for i, b in enumerate(magtag.peripherals.buttons):
                        if not b.value:
                            magtag_pixels[3-i] = pixelColors[3-i]
                            resetList[3-i] = True
            else:
                activateHallPass()

### --- RUNTIME CODE --- ###
setupDisplay()
activateHallPass()
buttonChecker()
pinAlarm = [
    alarm.pin.PinAlarm(pin=board.BUTTON_D, value=False, pull=True)
]
alarm.exit_and_deep_sleep_until_alarms(*pinAlarm)

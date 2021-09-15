from adafruit_magtag.magtag import MagTag
from adafruit_led_animation.color import RED, GREEN, BLUE, CYAN, WHITE,\
    OLD_LACE, PURPLE, MAGENTA, YELLOW, ORANGE, PINK
import time

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
pixelColors = [RED, ORANGE, YELLOW, GREEN]
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
    magtag.set_text('Null', index=0)
    magtag.set_text('Pass', index=1)
    passActive = False

# Initialize display
def setupDisplay():
    global magtag

    magtag.graphics.set_background('/background.bmp')

    magtag.add_text(
        text_scale=3,
        text_position=(
            (magtag.graphics.display.width // 2),
            220
        ),
        text_anchor_point=(0.5, 0.5)
    )
    magtag.add_text(
        text_scale=3,
        text_position=(
            (magtag.graphics.display.width // 2),
            250
        ),
        text_anchor_point=(0.5, 0.5)
    )
    resetDisplay()

# Get current time and activate Hall Pass
def activateHallPass():
    global magtag
    global passActive
    try:
        currentTime = ''
        currentTime = magtag.fetch()
        currentTime = currentTime.split(' ')
        flashNeo(GREEN)
        for i in range(2):
            magtag.set_text(currentTime[i], index=i)
        passActive = True
        # magtag.exit_and_deep_sleep(60)
    except (RuntimeError, ValueError) as e:
        print('Retrying - ', e)

### --- RUNTIME CODE --- ###

# Initliaze display (only run on first start)
setupDisplay()

# Main Loop
while True:

    # Loop through buttons, checking for input
    for i, b in enumerate(magtag.peripherals.buttons):

        # Try to connect to WiFi and activate the Hall Pass
        if not b.value and not passActive:
            try:
                magtag.network.connect()
                print('WiFi Success')
                activateHallPass()
            except ConnectionError as e:
                print("Retrying - ", e)
                flashNeo(RED)

        # If pass has been activated, listen for reset condition
        if passActive:
            magtag.peripherals.neopixel_disable = False
            if all(resetList):
                magtag.peripherals.neopixel_disable = True
                flashNeo(ORANGE)
                resetDisplay()
            if not b.value:
                magtag_pixels[3-i] = pixelColors[3-i]
                resetList[i] = True

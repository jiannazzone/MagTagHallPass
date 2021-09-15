# MagTagHallPass

This is for all of you teachers who are tired of writing hall passes! The **MagTag Hall Pass** will automatically fetch the current time from Adafruit IO and display it on the e-paper display. When the student returns, it can go into a deep sleep state, ready for the next user. I have not done extensive testing yet, but using one of the Adafruit Li-ion should provide several days of battery life (at least).

## Part List
* [Adafruit MagTag](https://www.adafruit.com/magtag)
* [Lithium-Ion Battery](https://www.adafruit.com/product/4237)
* 4x M3 screws
* [3D Printed Case](https://learn.adafruit.com/magtag-3d-printed-stand-case) (optional)
  * Download my custom mid-frame with a lanyard loop [here](https://thangs.com/aiannazzone/MagTag-Frame-with-loop-26023).

## Set up your MagTag
1. Follow [this tutorial](https://learn.adafruit.com/adafruit-magtag) on Adafruit. Ensure that you have the bootloader properly installed and can run the test code.
2. Update your `secrets.py` file with your SSID, password, and Adafruit IO credentials and copy it to the root of CIRCUITPY
3. Install the following libraries in CIRCUITPY/lib. **NOTE:** The libraries included in the source are for CircuitPython 6*. When you set up your board in Step 1, ensure that you download the correct library files for your version of CircuitPython if you are using a different version.
    * adafruit_bitmap_font/
    * adafruit_display_text/
    * adafruit_io/
    * adafruit_magtag/
    * adafruit_portalbase/
    * adafruit_fakerequests.mpy
    * adafruit_miniqr.mpy
    * adafruit_requests.mpy
    * neopixel.mpy
    * simpleio.mpy
4. Download code.py and install it to the root of CIRCUITPY

## Making a custom Background
If you would like a custom backround for your tag, you will need to create a 128x296 bitmap image and add your own. I used Adobe Photoshop and created the file in Greyscale mode. Name it `background.bmp` and install it to the root of CIRCUITPY.

## Secrets File
If you need a template for the secrets file, you can use this one and save it as `secrets.py` to the root of CIRCUITPY. If connecting to an open WiFi network, leave the password as `''` (no space). You will need an account at https://io.adafruit.com/ to get your `aio_username` and `aio_key`.
```
# This file is where you keep secret settings, passwords, and tokens!
# If you put them in the code you risk committing that info or sharing it

secrets = {
    'ssid' : 'home_wifi_network',
    'password' : 'wifi_password',
    'aio_username' : 'my_adafruit_io_username',
    'aio_key' : 'my_adafruit_io_key',
    'timezone' : "America/New_York", # http://worldtimeapi.org/timezones
    }
```

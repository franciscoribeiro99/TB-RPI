from rpi_ws281x import Adafruit_NeoPixel, Color

LED_COUNT      = 112
LED_PIN        = 18
LED_FREQ_HZ    = 800000
LED_DMA        = 10
LED_BRIGHTNESS = 65
LED_INVERT     = False
LED_CHANNEL    = 0

### CODE BASED ON https://learn.adafruit.com/neopixels-on-raspberry-pi

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA,
                          LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def set_all_leds(r, g, b):
    color = Color(r, g, b)
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def set_brightness(brightness):
    global strip
    strip.setBrightness(brightness)
    strip.show()

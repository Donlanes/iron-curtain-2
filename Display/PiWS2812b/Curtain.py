import sys
import math
from Display.DisplayInterface import DisplayInterface as DisplayInterface

import neopixel

class Curtain(DisplayInterface):
    def __init__(self, width, height):
        self.width = width
        self.height = height


        self._renderCells()

        LED_CHANNEL    = 0
        LED_COUNT      = width*height        # How many LEDs to light.
        LED_FREQ_HZ    = 800000     # Frequency of the LED signal.  Should be 800khz or 400khz.
        LED_DMA_NUM    = 5          # DMA channel to use, can be 0-14.
        LED_GPIO       = 18         # GPIO connected to the LED signal line.  Must support PWM!
        LED_BRIGHTNESS = 255        # Set to 0 for darkest and 255 for brightest
        LED_INVERT     = 0          # Set to 1 to invert the LED signal, good if using NPN
                                                                # transistor as a 3.3V->5V level converter.  Keep at 0
                                                            # for a normal/non-inverted signal.

        self.strip = neopixel.Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
	# Intialize the library (must be called once before other functions).
	self.strip.begin()
	
    def sendColorCanvas(self, canvas):
        for y in xrange(height):
            for x in xrange(width):
                self.strip.setPixelColor(i,neopixel.Color(canvas[y,x] & 255))
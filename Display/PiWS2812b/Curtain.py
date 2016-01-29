import sys
import math
from Display.DisplayInterface import DisplayInterface as DisplayInterface

import neopixel

ZIGZAG = True
RIGHT_FIRST = True
TOP_FIRST = True
class Curtain(DisplayInterface):
    def __init__(self, width, height, LED_DMA=5, LED_PIN = 18):
        self.width = width
        self.height = height


        LED_CHANNEL    = 0
        LED_COUNT      = width*height        # How many LEDs to light.
        LED_FREQ_HZ    = 800000     # Frequency of the LED signal.  Should be 800khz or 400khz.
        LED_BRIGHTNESS = 255        # Set to 0 for darkest and 255 for brightest
        LED_INVERT     = 0          # Set to 1 to invert the LED signal, good if using NPN
                                                                # transistor as a 3.3V->5V level converter.  Keep at 0
                                                            # for a normal/non-inverted signal.

        self.strip = neopixel.Adafruit_NeoPixel(LED_COUNT,
                                                LED_PIN,
                                                LED_FREQ_HZ,
                                                LED_DMA,
                                                LED_INVERT,
                                                LED_BRIGHTNESS)
        # Intialize the library (must be called once before other functions).
        self.strip.begin()
    
    def sendColorCanvas(self, canvas):
        isReversed = RIGHT_FIRST
        i=0
        height = self.height
        width = self.width
        for y in xrange(height):
            for x in xrange(width):
                if isReversed:
                    r,g,b= canvas[y,width-x-1]
                else:
                    r,g,b= canvas[y,x]
                r=int(r);g=int(g);b=int(b)
                self.strip.setPixelColor(i,neopixel.Color(r,g,b))
                i+=1
            isReversed=not isReversed

        self.strip.show()

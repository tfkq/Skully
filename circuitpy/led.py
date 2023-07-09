# import time
import board
# from rainbowio import colorwheel
import neopixel
import colorsys
from storage_management import *

already_off = False
previous_brightness = 0

pixel_pin = board.GP15
num_pixels = 50

pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=1.0, auto_write=False)

#* SETTINGS
def set_brightness(brightness):
    global already_off, previous_brightness
    previous_brightness = get_brightness()
    pixels.brightness = float(brightness)/100
    if float(brightness) > 0:
        already_off = False

def toggle():
    # log("toggle")
    if get_brightness() == 0:
        # log("toggle - LEDs ON")
        restore_brightness()
    else:
        # log("toggle - LEDs OFF")
        set_brightness(0)

def restore_brightness():
    set_brightness(previous_brightness)

def get_brightness():
    return pixels.brightness * 100

def get_previous_brightness():
    return previous_brightness

#* HELFERLEIN

def lerp(min, max, val):
    return (max-min)*val + min

def tri_lerp(min, middle, max, val):
    if val < 0.5:
        return 2 * (middle-min) * val + min
    elif val == 0.5:
        return middle
    elif val > 0.5:
        return 2*(max-middle)*val+(2*middle)-max

def vector_lerp(min, max, val):
    out = []
    for i in range(len(min)):
        out.append(lerp(min[i], max[i], val))
    return out

def vector_tri_lerp(min, middle, max, val):
    out = []
    for i in range(len(min)):
        out.append(tri_lerp(min[i], middle[i], max[i], val))
    return out

def hsv_to_grb_list(hsv: list):
    return hsv_to_grb(hsv[0], hsv[1], hsv[2])

def hsv_to_grb(hue: int, sat=100, value=100):
    if(sat == 0):
        x = value*255/100
        return [x, x, x]
    rgb = colorsys.hsv_to_rgb(hue/360, sat/100, value/100)
    grb = [rgb[1], rgb[0], rgb[2]]
    # log(rgb)
    return grb

def grb_to_hsv(grb):
    r, g, b = grb[1], grb[0], grb[2]
    # R, G, B values are divided by 255
    # to change the range from 0..255 to 0..1:
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    # h, s, v = hue, saturation, value
    cmax = max(r, g, b)    # maximum of r, g, b
    cmin = min(r, g, b)    # minimum of r, g, b
    diff = cmax-cmin       # diff of cmax and cmin.
    # if cmax and cmax are equal then h = 0
    if cmax == cmin: 
        h = 0
    # if cmax equal r then compute h
    elif cmax == r: 
        h = (60 * ((g - b) / diff) + 360) % 360
    # if cmax equal g then compute h
    elif cmax == g:
        h = (60 * ((b - r) / diff) + 120) % 360
    # if cmax equal b then compute h
    elif cmax == b:
        h = (60 * ((r - g) / diff) + 240) % 360
    # if cmax equal zero
    if cmax == 0:
        s = 0
    else:
        s = (diff / cmax) * 100
    # compute v
    v = cmax * 100
    return [h, s, v]

#* ACTUALLY LEDs

def off():
    global already_off
    if not already_off:
        already_off = True
        pixels.fill((0,0,0))
        pixels.show()
        # log("Turning off!")

def set_led(led: int, hue: int, light=100):
    pixels[led] = hsv_to_grb(hue, 100, light)
    
def set_led_grb(led:int, grb: list):
    pixels[led] = grb

def fill(grb: list):
    pixels.fill(grb)

def show():
    pixels.show()

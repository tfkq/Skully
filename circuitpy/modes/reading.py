import elements
import modes.super_mode as super_mode
import led
import math
import random

#* 

# GRB not RGB!
WHITE = (255, 255, 255)
WARM = (106, 255, 10)
CANDLE = (91, 255, 1)


class Reading(super_mode.SuperMode):
    
    def __init__(self, id="superMode", title="SuperMode", icon="sigma.svg") -> None:
        super().__init__(id, title, icon)
        self.color = "warm"
        self.animation = "none"
        self.g = 255
        self.r = 255
        self.b = 255
        self.color_values = (0,0,0)
        self.leds_hsv = [None]*50
        self.values = [0.4]*50
        self.decrements = [0]*50
        self.signs = [0]*50
        self.input("animation","flicker")

    def setup(self):
        # return super().setup()
        colors = [
            ["white", "Weiss"], ["warm", "Warmes Licht"], ["candle", "Kerzenschein"], ["custom", "Benutzerdefiniert"]
        ]
        self.elements.append(elements.RadioButtons(self.id, "color", "Farbton", colors, self.color))
        anims = [
            ["none", "Keine"], ["flicker", "Kerzenflackern"]
        ]
        self.elements.append(elements.RadioButtons(self.id, "animation", "Animation", anims, self.animation))
        self.elements.append(elements.Slider(self.id, "brightness", "Helligkeit", 0, 100, led.get_brightness()))
        self.elements.append(elements.Slider(self.id, "g", "G", 0, 255, self.g))
        self.elements.append(elements.Slider(self.id, "r", "R", 0, 255, self.r))
        self.elements.append(elements.Slider(self.id, "b", "B", 0, 255, self.b))

    def input(self, id, value):
        super().input(id, value)
        if id == "color":
            self.color = value
        elif id == "animation":
            self.animation = value
        elif id == "g":
            self.g = int(value)
        elif id == "r":
            self.r = int(value)
        elif id == "b":
            self.b = int(value)
        elif id == "brightness":
            led.set_brightness(int(value))
        
        self.color_values = None
        if self.color == "white":
            self.color_values = WHITE
        elif self.color == "warm":
            self.color_values = WARM
        elif self.color == "candle":
            self.color_values = CANDLE
        elif self.color == "custom":
            self.color_values = (self.g, self.r, self.b)

        hsv = led.grb_to_hsv(self.color_values)
        # print(self.col_values, hsv)
        hsv[2] = hsv[2]/1.5
        self.leds_hsv = [hsv]*50

    def update(self, counter):
        
        if self.animation == "none":
            led.fill(self.color_values)
        elif self.animation == "flicker":
            if random.random()*100 <= 5:
                n = int(random.random()*50)
                self.values[n] = min(random.random()*2, 1)
                self.decrements[n] = random.random()*0.001 + 0.01
                if self.values[n] > 0.5:
                    self.signs[n] = 1
                else:
                    self.signs[n] = 0

            for i in range(50):

                if self.values[i] > 0.2 and self.values[i] < 1:
                    self.values[i] += self.decrements[i] * (-1)**self.signs[i]
                    self.values[i] = min(self.values[i], 1)
                    self.values[i] = max(self.values[i], 0.2)

                grb = self.color_values
                grb = [grb[0]*self.values[i], grb[1]*self.values[i], grb[2]*self.values[i]]
                led.set_led_grb(i, grb)

        led.show()

    def get_dict(self):
        dict = super().get_dict()

        dict["color"] = self.color
        dict["animation"] = self.animation
        dict["g"] = self.g
        dict["r"] = self.r
        dict["b"] = self.b

        return dict
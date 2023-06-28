import elements
import modes.super_mode as super_mode
import led
import math
from storage_management import *

# * https://www.youtube.com/watch?v=0F1PrMyvjWc


class TriColor(super_mode.SuperMode):

    def __init__(self, id="superMode", title="SuperMode", icon="sigma.svg") -> None:
        super().__init__(id, title, icon)
        self.hue1 = 60
        self.hue2 = 180
        self.hue3 = 300
        self.grb1 = led.hsv_to_grb(self.hue1)
        self.grb2 = led.hsv_to_grb(self.hue2)
        self.grb3 = led.hsv_to_grb(self.hue3)
        self.animation = "wave"
        self.speed_breath = 30
        self.speed_wave = 20

    def setup(self):
        # return super().setup()
        self.elements.append(elements.ColorPicker(self.id, "color1", "Farbe 1", self.hue1, [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]))
        self.elements.append(elements.ColorPicker(self.id, "color2", "Farbe 2", self.hue2, [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]))
        self.elements.append(elements.ColorPicker(self.id, "color3", "Farbe 3", self.hue3, [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]))
        anims = [["breath", "Breathing"], ["wave", "Welle"]]
        self.elements.append(elements.RadioButtons(self.id, "animation", "Animation", anims, self.animation))
        self.elements.append(elements.Slider(self.id, "speed_breath", "Geschwindigkeit - Breath", 10, 100, self.speed_breath))
        self.elements.append(elements.Slider(self.id, "speed_wave", "Geschwindigkeit - Wave", 1, 100, self.speed_wave))

    def input(self, id, value):
        super().input(id, value)
        if id == "color1":
            self.hue1 = int(value)
            self.grb1 = led.hsv_to_grb(self.hue1)
        elif id == "color2":
            self.hue2 = int(value)
            self.grb2 = led.hsv_to_grb(self.hue2)
        elif id == "color3":
            self.hue3 = int(value)
            self.grb3 = led.hsv_to_grb(self.hue3)
        elif id == "animation":
            self.animation = value
        elif id == "speed_breath":
            self.speed_breath = float(value)
        elif id == "speed_wave":
            self.speed_wave = float(value)

    def update(self, counter):
        if self.animation == "breath":
            # log(self.grb1, self.grb2, led.vector_lerp(self.grb1, self.grb2, 0.5))
            val = 0.5 * math.cos(counter/self.speed_breath) + 0.5
            led.fill(led.vector_tri_lerp(self.grb1, self.grb2, self.grb3, val))
            # log(led.vector_lerp(self.grb1, self.grb2, counter/self.speed_breath))
        elif self.animation == "wave":
            for i in range(50):
                val = 0.5 * math.cos((counter-i*(2*math.pi*self.speed_wave/50))/self.speed_wave) + 0.5
                led.set_led_grb(i, led.vector_tri_lerp(self.grb1, self.grb2, self.grb3, val))
        led.show()

    def get_dict(self):
        dict = super().get_dict()

        dict["color1"] = self.hue1
        dict["color2"] = self.hue2
        dict["color3"] = self.hue3
        dict["animation"] = self.animation
        dict["speed_breath"] = self.speed_breath
        dict["speed_wave"] = self.speed_wave

        return dict
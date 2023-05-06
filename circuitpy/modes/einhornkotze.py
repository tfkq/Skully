import elements
import modes.super_mode as super_mode
import led
import math


#* UNICORN VOMIT


class Einhornkotze(super_mode.SuperMode):
    
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
        anims = [["breath", "Breathing"], ["wave", "Welle"]]
        self.elements.append(elements.RadioButtons(self.id, "animation", "Animation", anims, self.animation))
        self.elements.append(elements.Slider(self.id, "speed_breath", "Geschwindigkeit - Breath", 10, 100, self.speed_breath))
        self.elements.append(elements.Slider(self.id, "speed_wave", "Geschwindigkeit - Wave", 1, 100, self.speed_wave))

    def input(self, id, value):
        super().input(id, value)
        if id == "animation":
            self.animation = value
        elif id == "speed_breath":
            self.speed_breath = float(value)
        elif id == "speed_wave":
            self.speed_wave = float(value)

    def update(self, counter):
        if self.animation == "breath":
            # print(self.grb1, self.grb2, led.vector_lerp(self.grb1, self.grb2, 0.5))
            val = 180 * math.cos(counter/self.speed_breath) + 180
            led.fill(led.hsv_to_grb(val))
            # print(led.vector_lerp(self.grb1, self.grb2, counter/self.speed_breath))
        elif self.animation == "wave":
            for i in range(50):
                val = 180 * math.cos((counter-i*(2*math.pi*self.speed_wave/50))/self.speed_wave) + 180
                led.set_led_grb(i, led.hsv_to_grb(val))
        led.show()

    def get_dict(self):
        dict = super().get_dict()

        dict["animation"] = self.animation
        dict["speed_breath"] = self.speed_breath
        dict["speed_wave"] = self.speed_wave

        return dict
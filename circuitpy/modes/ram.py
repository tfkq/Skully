import modes.super_mode as super_mode
import elements
import led
import math

# * my name is giovanni gorgio, but everybody calls me gorgio


class RAM(super_mode.SuperMode):

    def __init__(self, id="superMode", title="SuperMode", icon="sigma.svg") -> None:
        super().__init__(id, title, icon)
        self.values = [0]*50
        self.cols = [[255,255,255]]*50
        self.cols[0] = [255,255,0]
        self.cols[1] = [255,255,0]
        self.cols[2] = [255,255,0]
        self.cols[3] = [255,255,0]
        self.cols[6] = [255,255,0]
        self.cols[7] = [255,255,0]
        self.cols[8] = [255,255,0]
        self.cols[10] = [255,255,0]
        self.cols[12] = [255,255,0]
        self.cols[13] = [255,255,0]
        self.cols[15] = [255,255,0]
        self.cols[16] = [255,255,0]
        self.cols[17] = [255,255,0]
        self.cols[20] = [255,255,0]
        self.cols[22] = [255,255,0]
        self.cols[24] = [255,255,0]
        self.cols[26] = [255,255,0]
        self.cols[29] = [255,255,0]
        self.cols[32] = [255,255,0]
        self.cols[33] = [255,255,0]
        self.cols[34] = [255,255,0]
        self.cols[36] = [255,255,0]
        self.cols[37] = [255,255,0]
        self.cols[38] = [255,255,0]
        self.cols[40] = [255,255,0]
        self.cols[43] = [255,255,0]
        self.cols[47] = [255,255,0]
        self.cols[48] = [255,255,0]
        self.cols[49] = [255,255,0]
        self.animation = "wave"
        self.speed_breath = 40
        self.speed_wave = 10
    
    def setup(self):
        # return super().setup()
        anims = [["none", "Keine"], ["breath", "Breathing"], ["wave", "Welle"]]
        self.elements.append(elements.RadioButtons(self.id, "animation", "Animation", anims, self.animation))
        self.elements.append(elements.Slider(self.id, "speed_breath", "Geschwindigkeit - Breath", 10, 100, self.speed_breath))
        self.elements.append(elements.Slider(self.id, "speed_wave", "Geschwindigkeit - Wave", 2, 50, self.speed_wave))

    def input(self, id, value):
        super().input(id, value)
        if id == "animation":
            self.animation = value
        elif id == "speed_breath":
            self.speed_breath = float(value)
        elif id == "speed_wave":
            self.speed_wave = float(value)
    
    def update(self, counter):
        # return super().update()
        if self.animation == "none":
            for i in range(50):
                self.values[i] = 100
        elif self.animation == "breath":
            light = (0.45*math.cos(counter/self.speed_breath)) + 0.55
            # print(counter, light)
            for i in range(50):
                self.values[i] = light
        elif self.animation == "wave":
            for i in range(50):
                light = (0.45* math.cos((counter-i*(2*math.pi*self.speed_wave/50))/self.speed_wave)) + 0.55
                self.values[i] = light

        for i in range(50):
            grb = self.cols[i]
            grb = [grb[0]*self.values[i], grb[1]*self.values[i], grb[2]*self.values[i]]
            led.set_led_grb(i, grb)

        led.show()

    def get_dict(self):
        dict = super().get_dict()

        dict["animation"] = self.animation
        dict["speed_breath"] = self.speed_breath
        dict["speed_wave"] = self.speed_wave

        return dict
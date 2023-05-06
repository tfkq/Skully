import elements
import modes.super_mode as super_mode
import led
import random

#* twinkle twinkle little star

WHITE = (255,255,255)
YELLOW = (255,255,0)

DECREMENT = 0.005

class Stars(super_mode.SuperMode):
    
    def __init__(self, id="superMode", title="SuperMode", icon="sigma.svg") -> None:
        super().__init__(id, title, icon)
        self.color = "yellow"
        self.color_code = YELLOW
        self.values = [0]*50
        self.decrements = [DECREMENT]*50
        self.signs = [0]*50

    def setup(self):
        # return super().setup()
        colors = [["white", "Weiss"], ["yellow", "Gelb"]]
        self.elements.append(elements.RadioButtons(self.id, "color", "Farbe", colors, self.color))

    def input(self, id, value):
        super().input(id, value)
        if id == "color":
            self.color = value
            if self.color == "white":
                self.color_code = WHITE
            elif self.color == "yellow":
                self.color_code = YELLOW

    def update(self, counter):

        if random.random()*100 <= 15:
            n = int(random.random()*50)
            self.values[n] = random.random()
            self.decrements[n] = random.random()*0.001 + 0.005
            if self.values[n] > 0.5:
                self.signs[n] = 1
            else:
                self.signs[n] = 0

        for i in range(50):

            if self.values[i] > 0 and self.values[i] < 1:
                self.values[i] += self.decrements[i] * (-1)**self.signs[i]
                self.values[i] = min(self.values[i], 1)
                self.values[i] = max(self.values[i], 0)

            grb = self.color_code
            grb = [grb[0]*self.values[i], grb[1]*self.values[i], grb[2]*self.values[i]]
            led.set_led_grb(i, grb)
        
        led.show()

    def get_dict(self):
        dict = super().get_dict()

        dict["color1"] = self.color
        return dict
 
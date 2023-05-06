import elements
import modes.super_mode as super_mode
import led
import random


GRB1 = [10,255,0]   # red
GRB3 = [60,255,0]   # orange
GRB2 = [175,255,0]  # yellow

class Fire(super_mode.SuperMode):
    
    def __init__(self, id="superMode", title="SuperMode", icon="sigma.svg") -> None:
        super().__init__(id, title, icon)
        self.values = [0]*50
        self.decrements = [0]*50
        self.signs = [0]*50
        self.speed = 20

    def setup(self):
        # return super().setup()
        # colors = [["white", "Weiss"], ["yellow", "Gelb"]]
        # self.elements.append(elements.RadioButtons(self.id, "color", "Farbe", colors, self.color))
        self.elements.append(elements.Slider(self.id, "Geschwindigkeit", "speed", 0, 100, self.speed))

    def input(self, id, value):
        super().input(id, value)
        if id == "speed":
            self.speed = int(value)

    def update(self, counter):
        pass

        if random.random()*100 <= 45:
            n = int(random.random()*50)
            self.values[n] = random.random()
            self.decrements[n] = random.random()*0.01 + 0.005
            if self.values[n] > 0.5:
                self.signs[n] = 1
            else:
                self.signs[n] = 0

        for i in range(50):

            if self.values[i] > 0 and self.values[i] < 1:
                self.values[i] += self.decrements[i] * (-1)**self.signs[i]

            grb = led.vector_tri_lerp(GRB1, GRB2, GRB3, self.values[i])
            led.set_led_grb(i, grb)
        
        led.show()

    def get_dict(self):
        dict = super().get_dict()

        dict["speed"] = self.speed

        return dict



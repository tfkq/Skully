import elements
import modes.super_mode as super_mode
import led
import math


class SingleColor(super_mode.SuperMode):

	def __init__(self, id="superMode", title="SuperMode", icon="sigma.svg") -> None:
		super().__init__(id, title, icon)
		self.hue = 120
		self.animation = "wave"
		self.speed_breath = 40
		self.speed_wave = 10
    
	def setup(self):
		# return super().setup()
		self.elements.append(elements.ColorPicker(self.id, "color", "Farbe", self.hue, [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]))
		anims = [["none", "Keine"], ["breath", "Breathing"], ["wave", "Welle"]]
		self.elements.append(elements.RadioButtons(self.id, "animation", "Animation", anims, self.animation))
		self.elements.append(elements.Slider(self.id, "speed_breath", "Geschwindigkeit - Breath", 10, 100, self.speed_breath))
		self.elements.append(elements.Slider(self.id, "speed_wave", "Geschwindigkeit - Wave", 2, 50, self.speed_wave))

	def input(self, id, value):
		super().input(id, value)
		if id == "color":
			self.hue = int(value)
		elif id == "animation":
			self.animation = value
		elif id == "speed_breath":
			self.speed_breath = float(value)
		elif id == "speed_wave":
			self.speed_wave = float(value)
	
	def update(self, counter):
		# return super().update()
		if self.animation == "none":
			for i in range(50):
				led.set_led(i, self.hue)
		elif self.animation == "breath":
			light = (45*math.cos(counter/self.speed_breath)) + 55
			# print(counter, light)
			for i in range(50):
				led.set_led(i, self.hue, light)
		elif self.animation == "wave":
			for i in range(50):
				light = (45* math.cos((counter-i*(2*math.pi*self.speed_wave/50))/self.speed_wave)) + 55
				led.set_led(i, self.hue, light)
		led.show()

	def get_dict(self):
		dict = super().get_dict()

		dict["color"] = self.hue
		dict["animation"] = self.animation
		dict["speed_breath"] = self.speed_breath
		dict["speed_wave"] = self.speed_wave

		return dict
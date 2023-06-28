from storage_management import *


class SuperElement:
    
	def __init__(self, mode_id, id, label) -> None:
		self.mode_id = mode_id
		self.id = id
		self.label = label
		self.current = 0

	def get_html(self) -> str:
		return "SuperElement: " + self.id + ", " + self.label + "<br>"
	
	def set_current(self, current):
		self.current = current
	

class ColorPicker(SuperElement):

	def __init__(self, mode_id, id, label, current, colors=[]) -> None:
		super().__init__(mode_id, id, label)
		self.current = current
		self.colors = colors

	def get_html(self) -> str:
		html = """
		<div class="el_color_picker">
		<label for="{0}">{1}: <span class="value_overview"><i>(Hue: <b>{2}</b>)</i></span></label>
		<br>
		<form accept-charset="utf-8" action="/?mode_config={4}" method="POST">
		<input type="range" min="0" max="360" value="{2}" class="hue_slider" id="{0}" name="{0}" onmouseup="this.form.submit();" ontouchend="this.form.submit();">
		</form>
		<form accept-charset="utf-8" action="/?mode_config={4}" method="POST">
		<div class="colors_flex_container">
		{3}
		</div>
		</form>
		</div>
		"""

		html_colors = ""
		if len(self.colors) != 0:
			html_colors += "<br>"
			for i in self.colors:
				sel = "class=\"color_buttons\" "
				if int(self.current) == int(i):
					sel = "class=\"color_buttons_selected\" "
				html_colors += """<button {2}style="background-color: hsl({0},100%, 50%)" value="{0}" name="{1}" type="submit">
				</button>""".format(i, self.id, sel)

		return html.format(self.id, self.label, self.current, html_colors, self.mode_id)
	
class Slider(SuperElement):

	def __init__(self, mode_id, id, label, min=0, max=100, current=0) -> None:
		super().__init__(mode_id, id, label)
		self.min = min
		self.max = max
		self.current = current
		self.start_value = current

	def get_html(self) -> str:
		html = """
		<div class="el_slider">
		<label for="{0}">{1}: <span class="value_overview"><i>(Bereich: {2}..{3} - Wert: <b>{4}</b> - Voreinstellung: {6})</i></span></label>
		<br>
		<form accept-charset="utf-8" action="/?mode_config={5}" method="POST">
 		<input type="range" min="{2}" max="{3}" value="{4}" class="slider" id="{0}" name="{0}" onmouseup="this.form.submit();" ontouchend="this.form.submit();">
		</form>
		</div>
		"""
		return html.format(self.id, self.label, self.min, self.max, self.current, self.mode_id, self.start_value)
	

class RadioButtons(SuperElement):

	def __init__(self, mode_id, id, label, options, current) -> None:
		super().__init__(mode_id, id, label)
		self.options = options
		self.current = current

	def get_html(self) -> str:
		html = """
		<div class="el_radio_buttons">
		 <label for="{0}">{1}:</label>
			<form id="{0}" accept-charset="utf-8" action="/?mode_config={2}" method="POST">
			"""
		
		for opt in self.options:
			id = opt[0]
			label = opt[1]
			if id == self.current:
				html += """<input type="radio" class="radio_button" id="{1}" name="{0}" value="{1}" checked type="submit" onchange="this.form.submit();">""".format(self.id, id, label)
			else:
				html += """<input type="radio" class="radio_button" id="{1}" name="{0}" value="{1}" type="submit" onchange="this.form.submit();">""".format(self.id, id, label)
			html += """<label for="{0}">{1}</label><br>""".format(id, label)

		html += "</form></div>"

		return html.format(self.id, self.label, self.mode_id)
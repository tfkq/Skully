import elements
import led

class SuperMode:
    def __init__(self, id="superMode", title="SuperMode", icon="sigma.svg") -> None:
        self.id = id
        self.title = title	# title of this mode
        
        file = open("./www/source/{0}".format(icon), "r")
        self.icon = ""
        for i in file.readlines():
            self.icon += i.strip()
        file.close()
        
        self.html_block = ""
        self.elements = []  # list of html-blocks on its settings page

    def setup(self):
        self.elements.append(elements.ColorPicker(self.id, "col", "Farbe", 0 , [0,60,120,180,240, 42,43,44,45,46,74,48,49,50]))
        self.elements.append(elements.ColorPicker(self.id, "col2", "Farbe2", 0 , [0,60,120,180,240]))
        self.elements.append(elements.ColorPicker(self.id, "col3", "Farbe3", 0))
        self.elements.append(elements.Slider(self.id, "slider", "Slider", 0, 3, 1))
        self.elements.append(elements.Slider(self.id, "slider2", "Slider2", 0, 100))
        options = [
            ["ls", "Luke Skywalker"],
            ["hs", "Han Solo"],
            ["ls2", "Leia Skywalker"],
            ["y", "Yoda"],
            ["dv", "Darth Vader"]
        ]
        self.elements.append(elements.RadioButtons(self.id, "rad", "StarWars", options, "hs"))
    
    # def set_html_block(self, html, settings_icon):
    #     self.html_block = html.format(self.icon, self.title, settings_icon)

    def input(self, id, value):
        for i in self.elements:
            if i.id == id:
                i.set_current(value)

    def update(self, counter):
        if counter % 10 < 5:
            led.fill((0,25,0))
        else:
            led.fill((25,25,25))
        led.show()

    # get the html for its own settings page
    def get_html_config(self) -> str:
        html = ""
        file = open("./www/mode_config.html", "r")
        for i in file.readlines():
            html += i.strip()
        file.close()

        css_style = ""
        file = open("./www/config_style.css", "r")
        for i in file.readlines():
            css_style += i.strip()
        file.close()

        elements = ""
        for i in self.elements:
            elements += i.get_html()

        return html.format(css_style, self.icon, self.title, elements)

    # get the html block for the main page
    def get_html_block(self, html, settings_icon) -> str:
        return html.format(self.icon, self.title, settings_icon, self.id)
    
    def get_dict(self):

        dict = {}
        dict["id"] = self.id

        return dict

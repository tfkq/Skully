import gc
import os
import ipaddress
import wifi
import socketpool
import time
import microcontroller
import board
from digitalio import DigitalInOut, Direction, Pull
import ssl
import adafruit_requests
from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.methods import HTTPMethod
from adafruit_httpserver.mime_type import MIMEType

import storage_management as sto
import led

# import modes.super_mode as super_mode
import modes.bicolor as bicolor
import modes.einhornkotze as einhornkotze
import modes.fire as fire
import modes.ram as ram
import modes.reading as reading
import modes.single_color as single_color

# import modes.snow as snow
import modes.stars as stars
import modes.tricolor as tricolor

# * VARIABLES

ip = ""
ip_with_buttons = "192.168.178.221"
ip_without_buttons = "192.168.178.220"
enable_smartphone_search = True
ip_of_smartphone = ipaddress.ip_address("192.168.178.20")

modes = []
modes.append(
    single_color.SingleColor("singleColor", "Eine Farbe", "numeric-1-circle.svg")
)
modes.append(bicolor.BiColor("biColor", "Zwei Farben", "numeric-2-circle.svg"))
modes.append(tricolor.TriColor("triColor", "Drei Farben", "numeric-3-circle.svg"))
modes.append(reading.Reading("read", "Leselicht", "desk-lamp-on.svg"))
modes.append(fire.Fire("fire", "Feuer", "fire.svg"))
modes.append(stars.Stars("star", "Sternenhimmel", "star.svg"))
modes.append(einhornkotze.Einhornkotze("unicorn", "Regenbogen", "unicorn.svg"))

cur_mode = 4


for i in modes:
    i.setup()

# * HELPER FUNCTIONS


def next_mode():
    global cur_mode
    cur_mode += 1
    if cur_mode >= len(modes):
        cur_mode = 0
    print("NEW MODE: ", cur_mode, modes[cur_mode].title)


def reading_mode():
    global cur_mode
    for idx, mode in enumerate(modes):
        if mode.id == "read":
            print("NEW MODE: ", idx, mode.title)
            cur_mode = idx
            break


# * SETUP - WIFI/SERVER
print()
print("Connecting to WiFi")
#  connect to your SSID
wifi.radio.connect(
    os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD")
)
print("Connected to WiFi")
pool = socketpool.SocketPool(wifi.radio)
#  prints MAC address to REPL
print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
#  prints IP address to REPL
print("My IP address is", wifi.radio.ipv4_address)
ip = str(wifi.radio.ipv4_address)
#  pings Google
ipv4_ping = ipaddress.ip_address("8.8.4.4")
print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4_ping) * 1000))
print("starting server..")
# startup the server
pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

# * SETUP - WEBSITE

if not ip == ip_with_buttons:
    modes.append(ram.RAM("ram", "RAM", "daft.svg"))

# for i in modes:
#     i.set_html_block(html_mode_block, svg_settings_icon)
# print("read the files")

#  route default static IP
@server.route("/")
def base(request: HTTPRequest):  # pylint: disable=unused-argument
    global modes, cur_mode

    sto.request_config_save()
    gc.collect()

    print("request incoming...")

    if "action" in request.query_params:

        ok = True

        param = request.query_params["action"]
        if param == "toggle_power":
            led.toggle()

        elif param == "toggle_power_0":
            led.set_brightness(0)

        elif param == "toggle_power_1":
            led.set_brightness(100)

        elif param == "next_mode":
            next_mode()

        elif param == "reading_mode":
            reading_mode()

        else:
            ok = False

        text = ""
        if ok:
            text = "Thank you!"
        else:
            text = "Don't know what you talkin' about"
        with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
            response.send(text)

    elif "mode_config" in request.query_params:

        new_mode = request.query_params["mode_config"]
        for idx, mode in enumerate(modes):
            if mode.id == new_mode:
                print("NEW MODE: ", idx, mode.title)
                cur_mode = idx
                break

        text = modes[cur_mode].get_html_config()

        with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
            response.send(text)

    else:

        if "mode_start" in request.query_params:
            new_mode = request.query_params["mode_start"]
            for idx, mode in enumerate(modes):
                if mode.id == new_mode:
                    print("NEW MODE: ", idx, mode.title)
                    cur_mode = idx
                    break

        # TODO optimize runtime, have these files constantly in ram ?
        css_style = ""
        file = open("./www/style.css", "r")
        for i in file.readlines():
            css_style += i.strip()
        file.close()

        html_index = ""
        file = open("./www/index.html", "r")
        for i in file.readlines():
            html_index += i.strip()
        file.close()

        html_mode_block = ""
        file = open("./www/mode_block.html", "r")
        for i in file.readlines():
            html_mode_block += i.strip()
        file.close()

        svg_settings_icon = ""
        file = open("./www/source/cog.svg", "r")
        for i in file.readlines():
            svg_settings_icon += i.strip()
        file.close()

        # gc.collect()

        html_modes = ""
        for i in modes:
            html_modes += i.get_html_block(html_mode_block, svg_settings_icon)

        #  serve the HTML f string
        #  with content type text/html
        gc.collect()
        with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
            gc.collect()
            response.send(
                html_index.format(
                    css_style,
                    html_modes,
                    str(led.get_brightness()),
                    str(led.get_previous_brightness()),
                )
            )


@server.route("/", method=HTTPMethod.POST)
def post(request: HTTPRequest):
    global brightness

    sto.request_config_save()
    gc.collect()
    req = request.raw_request.decode("UTF-8")
    # print(req)

    # we expect something along the lines of this:

    # POST /?mode_config=singleColor HTTP/1.1
    # Host: 192.168.178.220
    # User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0
    # Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
    # Accept-Language: de,en;q=0.5
    # Accept-Encoding: gzip, deflate
    # Content-Type: application/x-www-form-urlencoded
    # Content-Length: 6
    # Origin: http://192.168.178.220
    # DNT: 1
    # Connection: keep-alive
    # Referer: http://192.168.178.220/?mode_config=singleColor
    # Upgrade-Insecure-Requests: 1
    #
    # col=60

    # we look in the first line for the mode, and the last line for element id and its value

    first_line = req.splitlines()[0]
    last_line = req.splitlines()[-1]

    # print(first_line)
    # print(last_line)

    # there might no "=" in the first line, because its the brightness level
    if not "=" in first_line and last_line[: last_line.find("=")] == "brightness":
        led.set_brightness(last_line[last_line.find("=") + 1 :])

    else:
        mode = first_line[first_line.find("=") + 1 :]
        mode = mode[: mode.find(" ")]
        id = last_line[: last_line.find("=")]
        value = last_line[last_line.find("=") + 1 :]

        # print("MODE: \"" + mode + "\"")
        # print("ID:   \"" + id + "\"")
        # print("VALUE:\"" + value + "\"")

        for i in modes:
            if i.id == mode:
                i.input(id, value)

    base(request)


try:
    server.start(str(wifi.radio.ipv4_address))
    print("Listening on http://%s:80" % wifi.radio.ipv4_address)
#  if the server fails to begin, restart the pico w
except OSError:
    time.sleep(5)
    print("restarting..")
    microcontroller.reset()
ping_address = ipaddress.ip_address("8.8.4.4")

# * SETUP CONFIG SAVE // LOAD CONFIG

cur_mode, b = sto.load_config(modes)
led.set_brightness(b)

# * SETUP - BUTTONS

btn_next_prev_value = False
btn_next = DigitalInOut(board.GP28)
btn_next.direction = Direction.INPUT
btn_next.pull = Pull.UP

btn_read_prev_value = False
btn_read = DigitalInOut(board.GP27)
btn_read.direction = Direction.INPUT
btn_read.pull = Pull.UP

btn_power_prev_value = False
btn_power = DigitalInOut(board.GP26)
btn_power.direction = Direction.INPUT
btn_power.pull = Pull.UP

if ip == ip_with_buttons:
    print("i'm the one with buttons!")

led_builtin = DigitalInOut(board.LED)
led_builtin.direction = Direction.OUTPUT

# * SETUP - TIMER

start_time = time.monotonic() * 1000


def get_millis():
    return time.monotonic() * 1000 - start_time

smartphone_ping_last_update_time = 0    # timing things, to ping at an interval
smartphone_ping_update_every = 1000*60 # ms
smartphone_ping_last_found = 0  # the last time the smartphone was found
smartphone_ping_timeout = 1000*60*10  # [ms], the time it takes for the LEDs to turn off

last_update_time = 0
updates_every = 30  # ms
counter = 0

while True:

    # * ### CHECK THE BUTTONS

    if ip == ip_with_buttons:
        val = btn_next.value
        if btn_next_prev_value != val:
            btn_next_prev_value = val
            print("🟡 Next Button:", val)
            if val == False:
                sto.request_config_save()
                next_mode()
        val = btn_read.value
        if btn_read_prev_value != val:
            btn_read_prev_value = val
            print("🟡 Read Button:", val)
            if val == False:
                sto.request_config_save()
                reading_mode()
        val = btn_power.value
        if btn_power_prev_value != val:
            btn_power_prev_value = val
            print("🟡 Power Button:", val)
            if val == False:
                sto.request_config_save()
                led.toggle()
                if led.get_brightness() != 0:
                    modes[cur_mode].update(counter)
                else:
                    led.off()
                url = "http://" + ip_without_buttons + "/?action=toggle_power_"
                if led.get_brightness() == 0:
                    url += "0"
                else:
                    url += "1"
                try:
                    r = requests.get(url, timeout=10)
                except RuntimeError:
                    print("[ERR] couldn't reach Skully")

    # * ### CHECK THE LEDS

    if last_update_time + updates_every <= get_millis():
        last_update_time = get_millis()

        # Neopixels
        if led.get_brightness() != 0:
            modes[cur_mode].update(counter)
        else:
            led.off()

        # Read/Write Status
        if not sto.get_writing_allowed():
            if counter % 10 < 5:
                led_builtin.value = True
            else:
                led_builtin.value = False
        else:
            led_builtin.value = False

        # Counter
        counter += 1
        # print(counter)
        if counter >= 1073741823:
            counter = 0
            print("kinda-annual counter reset 🎉")
        if counter >= 2880000 and led.get_brightness() == 0:
            counter = 0
        # print(get_millis())

    # * ### CHECK THE SERVER AND OTHER STUFF

    server.poll()

    # test connection
    # print(wifi.radio.ipv4_address)

    if wifi.radio.ipv4_address == None:
        print("internet futsch")
        pass
        try:
            wifi.radio.connect(
                os.getenv("CIRCUITPY_WIFI_SSID"),
                os.getenv("CIRCUITPY_WIFI_PASSWORD"),
                timeout=10,
            )
        except ConnectionError as c:
            print(c)

    # ping my smartphone

    if enable_smartphone_search:
        if smartphone_ping_last_update_time + smartphone_ping_update_every <= get_millis():
            smartphone_ping_last_update_time = get_millis()
            try:
                ans = (wifi.radio.ping(ip_of_smartphone) * 1000)
                if(type(ans) == float):
                    # print("smartphones there!")
                    if (led.get_brightness() == 0):
                        print("📱 smartphone back, turning back on!")
                        led.restore_brightness()
                    smartphone_ping_last_found = get_millis()
            except TypeError as t:
                # print(t)
                # print("smartphones NOT there!")
                pass

            if(smartphone_ping_last_found+ smartphone_ping_timeout < get_millis()):
                if(led.get_brightness() > 0):
                    print("📱 Smartphone gone for too long, turning off!")
                    led.set_brightness(0)


    # update cong
    sto.update(led_builtin, cur_mode, modes)

    gc.collect()
    # print(gc.mem_free())

import adafruit_requests
from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.request import HTTPRequest
from adafruit_httpserver.response import HTTPResponse
from adafruit_httpserver.methods import HTTPMethod
from adafruit_httpserver.mime_type import MIMEType
import wifi
import socketpool
import ssl
import gc
import os
import ipaddress
import time
import microcontroller
import board
from digitalio import DigitalInOut, Direction, Pull
import storage_management as sto
from storage_management import *
import led
import modes.bicolor as bicolor
import modes.einhornkotze as einhornkotze
import modes.fire as fire
import modes.ram as ram
import modes.reading as reading
import modes.single_color as single_color
import modes.stars as stars
import modes.tricolor as tricolor

# * VARIABLES

ip = ""
ip_with_buttons = "192.168.178.52"
ip_without_buttons = "192.168.178.51"
enable_smartphone_search = True
ip_of_smartphone = ipaddress.ip_address("192.168.178.49")

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

crash_me = False
reboot_me = False

# * HELPER FUNCTIONS


def next_mode():
    global cur_mode
    cur_mode += 1
    if cur_mode >= len(modes):
        cur_mode = 0
    log("NEW MODE: ", cur_mode, modes[cur_mode].title)


def reading_mode():
    global cur_mode
    for idx, mode in enumerate(modes):
        if mode.id == "read":
            log("NEW MODE: ", idx, mode.title)
            cur_mode = idx
            break


# * SETUP - WIFI/SERVER
log()
log("Connecting to WiFi")
#  connect to your SSID
wifi.radio.connect(
    os.getenv("CIRCUITPY_WIFI_SSID"), os.getenv("CIRCUITPY_WIFI_PASSWORD")
)
log("Connected to WiFi")
pool = socketpool.SocketPool(wifi.radio)
#  prints MAC address to REPL
log("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
#  prints IP address to REPL
log("My IP address is", wifi.radio.ipv4_address)
ip = str(wifi.radio.ipv4_address)
#  pings Google
ipv4_ping = ipaddress.ip_address("8.8.4.4")
log("Ping google.com: %f ms" % (wifi.radio.ping(ipv4_ping) * 1000))
log("starting server..")
# startup the server
pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)
requests = adafruit_requests.Session(pool, ssl.create_default_context())
sto.ntp_setup(pool)

# * SETUP - WEBSITE

if not ip == ip_with_buttons:
    modes.append(ram.RAM("ram", "RAM", "daft.svg"))


#  route default static IP
@server.route("/")
def base(request: HTTPRequest):
    global modes, cur_mode

    sto.request_config_save()
    gc.collect()

    log("request incoming...")

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
                log("NEW MODE: ", idx, mode.title)
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
                    log("NEW MODE: ", idx, mode.title)
                    cur_mode = idx
                    break

        gc.collect()

        # TODO optimize runtime, have these files constantly in ram ?

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

        gc.collect()

        # TODO split transmission into several files
        html_modes = ""
        for i in modes:
            html_modes += i.get_html_block(html_mode_block)

        gc.collect()

        html_index = html_index.format(
            html_modes,
            str(led.get_brightness()),
            str(led.get_previous_brightness()),
        )

        #  serve the HTML string
        #  with content type text/html
        with HTTPResponse(request, content_type=MIMEType.TYPE_HTML) as response:
            # gc.collect()
            response.send(html_index)
    gc.collect()


@server.route("/style.css")
def serve_css(request: HTTPRequest):
    gc.collect()
    css_style = ""
    file = open("./www/style.css", "r")
    for i in file.readlines():
        css_style += i.strip()
    file.close()
    with HTTPResponse(
        request,
        content_type=MIMEType.TYPE_CSS,
        headers={"Cache-Control": "max-age=3600"},
    ) as response:
        response.send(css_style)
    gc.collect()


@server.route("/config_style.css")
def serve_config_css(request: HTTPRequest):
    gc.collect()
    css_style = ""
    file = open("./www/config_style.css", "r")
    for i in file.readlines():
        css_style += i.strip()
    file.close()
    with HTTPResponse(
        request,
        content_type=MIMEType.TYPE_CSS,
        headers={"Cache-Control": "max-age=604800"},
    ) as response:
        response.send(css_style)
    gc.collect()

content_source_dir = os.listdir("www/source")

@server.route("/source/")
@server.route("/source")
def serve_sources(request: HTTPRequest):
    gc.collect()
    # print("source request incoming...")
    if "file" in request.query_params:
        param = request.query_params["file"]
        if param in content_source_dir:
            source_file = ""
            file = open("./www/source/" + param, "r")
            for i in file.readlines():
                source_file += i.strip()
            file.close()
            with HTTPResponse(
                request,
                content_type=MIMEType.TYPE_SVG,
                headers={"Cache-Control": "max-age=604800"},
            ) as response:
                response.send(source_file)
        else:
            with HTTPResponse(
                request, content_type=MIMEType.TYPE_SVG, status=[404, "Not Found"]
            ) as response:
                response.send()
    else:
        with HTTPResponse(
            request, content_type=MIMEType.TYPE_HTML, status=[400, "Bad Request"]
        ) as response:
            response.send()

    gc.collect()


@server.route("/log")
def serve_config_css(request: HTTPRequest):
    gc.collect()
    log_file = ""
    file = open("./log", "r")
    for i in file.readlines():
        log_file += i.strip()
    file.close()
    with HTTPResponse(
        request, content_type=MIMEType.TYPE_HTML, headers={"Cache-Control": "no-store"}
    ) as response:
        response.send(log_file)
    gc.collect()


@server.route("/crash")
def crash(request: HTTPRequest):
    global crash_me
    crash_me = True
    with HTTPResponse(
        request, content_type=MIMEType.TYPE_HTML, headers={"Cache-Control": "no-store"}
    ) as response:
        response.send("hehe yeah boy")
    gc.collect()


@server.route("/reboot")
def reboot_request(request: HTTPRequest):
    global reboot_me
    reboot_me = True
    with HTTPResponse(
        request, content_type=MIMEType.TYPE_HTML, headers={"Cache-Control": "no-store"}
    ) as response:
        response.send("I'll see you on the other side...")
    log("❌ going to reboot (request)")
    gc.collect()


@server.route("/", method=HTTPMethod.POST)
def post(request: HTTPRequest):
    global brightness

    sto.request_config_save()
    gc.collect()
    req = request.raw_request.decode("UTF-8")
    # log(req)

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

    # log(first_line)
    # log(last_line)

    # there might no "=" in the first line, because its the brightness level
    if not "=" in first_line and last_line[: last_line.find("=")] == "brightness":
        led.set_brightness(last_line[last_line.find("=") + 1 :])

    else:
        mode = first_line[first_line.find("=") + 1 :]
        mode = mode[: mode.find(" ")]
        id = last_line[: last_line.find("=")]
        value = last_line[last_line.find("=") + 1 :]

        # log("MODE: \"" + mode + "\"")
        # log("ID:   \"" + id + "\"")
        # log("VALUE:\"" + value + "\"")

        for i in modes:
            if i.id == mode:
                i.input(id, value)

    base(request)
    gc.collect()


try:
    server.start(str(wifi.radio.ipv4_address))
    log("Listening on http://%s:80" % wifi.radio.ipv4_address)
#  if the server fails to begin, restart the pico w
except OSError:
    time.sleep(5)
    log("restarting..")
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
    log("i'm the one with buttons!")

led_builtin = DigitalInOut(board.LED)
led_builtin.direction = Direction.OUTPUT

# * SETUP - TIMER

start_time = time.monotonic() * 1000


def get_millis():
    return time.monotonic() * 1000 - start_time


smartphone_ping_last_update_time = 0  # timing things, to ping at an interval
smartphone_ping_update_every = 1000 * 60  # ms
smartphone_ping_last_found = 0  # the last time the smartphone was found
smartphone_ping_timeout = (
    1000 * 60 * 10
)  # [ms], the time it takes for the LEDs to turn off
off_because_smartphone = False

last_update_time = 0
updates_every = 30  # ms
counter = 0

# try:
if True:
    while True:
        # * ### CHECK THE BUTTONS

        if ip == ip_with_buttons:
            val = btn_next.value
            if btn_next_prev_value != val:
                btn_next_prev_value = val
                log("🟡 Next Button:", val)
                if val == False:
                    sto.request_config_save()
                    next_mode()
            val = btn_read.value
            if btn_read_prev_value != val:
                btn_read_prev_value = val
                log("🟡 Read Button:", val)
                if val == False:
                    sto.request_config_save()
                    reading_mode()
            val = btn_power.value
            if btn_power_prev_value != val:
                btn_power_prev_value = val
                log("🟡 Power Button:", val)
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
                        log("[ERR] couldn't reach Skully")

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
            # log(counter)
            if counter >= 1073741823:
                counter = 0
                log("kinda-annual counter reset 🎉")
            if counter >= 2880000 and led.get_brightness() == 0:
                counter = 0
            # log(get_millis())

        # * ### CHECK THE SERVER AND OTHER STUFF

        try:
            server.poll()
        except Exception as e:
            log(e)

        # test connection
        # log(wifi.radio.ipv4_address)

        if wifi.radio.ipv4_address == None:
            log("internet futsch")
            pass
            try:
                wifi.radio.connect(
                    os.getenv("CIRCUITPY_WIFI_SSID"),
                    os.getenv("CIRCUITPY_WIFI_PASSWORD"),
                    timeout=10,
                )
            except ConnectionError as c:
                log(c)

        # ping my smartphone

        if enable_smartphone_search:
            if (
                smartphone_ping_last_update_time + smartphone_ping_update_every
                <= get_millis()
            ):
                smartphone_ping_last_update_time = get_millis()
                try:
                    ans = wifi.radio.ping(ip_of_smartphone) * 1000
                    if type(ans) == float:
                        # log("smartphones there!")
                        if led.get_brightness() == 0 and off_because_smartphone:
                            log("📱 smartphone back, turning back on!")
                            led.restore_brightness()
                            off_because_smartphone = False
                        smartphone_ping_last_found = get_millis()
                except TypeError as t:
                    # log(t)
                    # log("smartphones NOT there!")
                    pass

                if smartphone_ping_last_found + smartphone_ping_timeout < get_millis():
                    if led.get_brightness() > 0:
                        log("📱 Smartphone gone for too long, turning off!")
                        led.set_brightness(0)
                        off_because_smartphone = True

        if crash_me:
            s = "a"
            i = 1
            while True:
                print(i)
                i = i + 1
                s = s + s

        if get_millis() > 1000 * 60 * 60 * 24 and led.get_brightness() == 0:
            reboot_me = True
            log("❌ going to reboot (timeout)")

        if reboot_me:
            log("❌ rebooting now...")
            microcontroller.reset()

        # update config
        sto.update(led_builtin, cur_mode, modes)

        # print(gc.mem_free())
        gc.collect()

# except Exception as e:
#     log(e)
#     log("Exiting...")

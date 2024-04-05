import json
import led
import adafruit_ntp
import gc
import time

_allow_writing = False
_request_save = False
_last_save = 0
COOLDOWN = 60

ntp = None


# * Log
def log(*args):
    gc.collect()
    if _allow_writing and False:
        s = "<p>"
        if ntp != None:
            t = ntp.datetime
            s += (
                "<i>["
                + str(t.tm_year)
                + "-"
                + str(t.tm_mon)
                + "-"
                + str(t.tm_mday)
                + " "
                + str(t.tm_hour)
                + ":"
                + str(t.tm_min)
                + ":"
                + str(t.tm_sec)
                + "]</i> "
            )
        else:
            s += "<i>[????-??-?? ??:??:??]</i> "

        for i in args:
            s += str(i) + " "
        s += "</p>\n"
        with open("/log", "a") as fp:
            fp.write(s)
            fp.flush()

    print(*args)


# * SETUP

try:
    log("💾 trying to write to a file")
    _allow_writing = True
    with open("/temp", "a") as fp:
        # fp.write("a\n")
        fp.flush()
except OSError as e:
    _allow_writing = False
    log("💾 writing failed, readonly mode")

if _allow_writing:
    log("💾 writing successful, read/write mode")


def ntp_setup(pool):
    global ntp
    ntp = adafruit_ntp.NTP(pool, tz_offset=0)


# * METHODS
def get_writing_allowed():
    return _allow_writing


def request_config_save():
    global _request_save
    if _allow_writing:
        _request_save = True
        log("💾 save request accepted")


def update(led_builtin, cur_mode, modes):
    global _request_save, _last_save
    gc.collect()
    # print(time.monotonic())
    if _request_save and _last_save + COOLDOWN < time.monotonic():
        _request_save = False
        led_builtin.value = True
        log("💾 fulfilling save request")
        _last_save = time.monotonic()

        # create dict
        dict = {}
        dict["cur_mode"] = cur_mode
        dict["brightness"] = led.get_brightness()

        list_modes = []

        for m in modes:
            list_modes.append(m.get_dict())

        dict["modes"] = list_modes

        # and convert into json
        js = json.dumps(dict)

        # log(js)

        # write file
        if _allow_writing:
            try:
                with open("/internal/config.json", "w") as fp:
                    fp.write(js)
                    fp.flush()
                    fp.close()
            except Exception as e:
                log("writing failed:")
                log(e)

        else:
            log("writing failed, not allowed!")

        led_builtin.value = False
    gc.collect()


def load_config(modes):
    gc.collect()
    log("loading config...")

    # read the file

    try:
        with open("/internal/config.json", "r") as fp:
            cnt = fp.readlines()
            fp.close()
    except Exception as e:
        log("reading file failed:")
        log(e)
        return 0, 100

    js = ""
    for l in cnt:
        js = js + l

    dict = json.loads(js)

    try:
        cur_mode = dict["cur_mode"]
        brightness = dict["brightness"]

        for m in dict["modes"]:  # current mode in json
            for i in modes:  # search all modes
                if i.id == m["id"]:  # to find the one with correct id
                    for k in m.keys():  # go through all the keys in json
                        if k != "id":  # except id
                            i.input(k, m[k])  # and put them into the actual mode-object

    except Exception as e:
        log("loading config failed:")
        log(e)
        return 0, 100

    print("done")
    gc.collect()
    return cur_mode, brightness

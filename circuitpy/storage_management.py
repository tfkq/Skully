import json
import board
from digitalio import DigitalInOut, Direction, Pull
import led


_allow_writing = True
_request_save = False
_last_save = 0
COOLDOWN = 5000

#* SETUP
for p in [board.GP13, board.GP14]:
    pin = DigitalInOut(p)
    pin.direction = Direction.INPUT
    pin.pull = Pull.UP
    print(pin.value)

try:
    print("💾 trying to write to a file")
    with open("/temp", "a") as fp:
        # fp.write("a\n")
        fp.flush()
except OSError as e:
    print("💾 writing failed, readonly mode")
    _allow_writing = False

if _allow_writing:
    print("💾 writing successful, read/write mode")

#* METHODS
def get_writing_allowed():
    return _allow_writing

def request_config_save():
    global _request_save
    if _allow_writing:
        _request_save = True
        print("💾 save request accepted")


def update(led_builtin, cur_mode, modes):
    global _request_save

    if _request_save:
        _request_save = False
        led_builtin.value = True
        print("💾 fulfilling save request")

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

        # print(js)

        # write file
        if _allow_writing:

            try:
                with open("/internal/config.json", "w") as fp:
                    fp.write(js)
                    fp.flush()
                    fp.close()
            except Exception as e:
                print("💾 writing failed:")
                print(e)
        
        else:
            print("💾 writing failed, not allowed!")


        led_builtin.value = False


def load_config(modes):
    print("💾 loading config...")

    # read the file 

    try:
        with open("/internal/config.json", "r") as fp:
            cnt = fp.readlines()
            fp.close()
    except Exception as e:
        print("💾 reading file failed:")
        print(e)
        return 0, 100
    
    js = ""
    for l in cnt:
        js = js+l

    dict = json.loads(js)

    try:
        cur_mode = dict["cur_mode"]
        brightness = dict["brightness"]

        for m in dict["modes"]: # current mode in json
            for i in modes:     # search all modes
                if i.id == m["id"]:    # to find the one with correct id
                    for k in m.keys():  # go through all the keys in json
                        if k != "id":   # except id
                            i.input(k, m[k])   # and put them into the actual mode-object

    except Exception as e:
        print("💾 loading config failed:")
        print(e)
        return 0, 100

    return cur_mode, brightness
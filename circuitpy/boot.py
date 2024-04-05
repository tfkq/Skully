import storage
import board
from digitalio import DigitalInOut, Direction, Pull

# * ###################
# * # MAKE A BACKUP ! #
# * ###################


readonly = False

for p in [
    board.GP1,
    board.GP2,
    board.GP5,
    board.GP6,
    board.GP9,
    board.GP10,
    board.GP13,
    board.GP14,
]:
    pin = DigitalInOut(p)
    pin.direction = Direction.INPUT
    pin.pull = Pull.UP

    print(p, pin.value)

    if pin.value == False:
        readonly = True

print("readonly =", readonly)

storage.remount("/", readonly)

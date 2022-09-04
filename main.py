from picographics import PicoGraphics, DISPLAY_TUFTY_2040, PEN_RGB332
from os import listdir
import time, gc
from pimoroni import Button

display = PicoGraphics(display=DISPLAY_TUFTY_2040, pen_type=PEN_RGB332, rotate=180)


def hsv_to_rgb(h, s, v):
    if s == 0.0:
        return v, v, v
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
    v = int(v * 255)
    t = int(t * 255)
    p = int(p * 255)
    q = int(q * 255)
    i = i % 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q


def get_applications():
    # fetch a list of the applications that are stored in the filesystem
    applications = []
    for file in listdir():
        if (file.endswith(".py") or file.endswith(".mpy")) and file != "main.py":  # include .mpy here!
            # convert the filename from "something_or_other.py" to "Something Or Other"
            # via weird incantations and a sprinkling of voodoo
            title = " ".join([v[:1].upper() + v[1:] for v in file[:-3].split("_")])

            applications.append(
                {
                    "file": file,
                    "title": title
                }
            )

    # sort the application list alphabetically by title and return the list
    return sorted(applications, key=lambda x: x["title"])


def launch_application(application):
    # wait_for_user_to_release_buttons()
    try:
        for k in locals().keys():
            if k not in ("gc", "file", "badger_os"):
                del locals()[k]

        gc.collect()

        __import__(application["file"])
    except Exception as ex:
        print(ex)


applications = get_applications()
# display.set_font("sans")

# Reads name from file, and then closes the file.
# try:
#     file = open("badge.txt", "r")
#     name = file.readline()
#     file.close()
# //except OSError:
# //    name = "open name.txt in thonny to edit badge :)"

# Tufty constants
# A = 7
# B = 8
# C = 15
# UP = 22
# DOWN = 6
# LED = 25

button_up = Button(22, invert=False)
button_down = Button(6, invert=False)
button_a = Button(7, invert=False)

display.set_backlight(1.0)

WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
RED = display.create_pen(200, 0, 0)


def text(text, x, y, pen, s):
    display.set_pen(pen)
    display.text(text, x, y, -1, s)


selected_item = 2
scroll_position = 2
target_scroll_position = 2

selected_pen = display.create_pen(255, 255, 255)
unselected_pen = display.create_pen(80, 80, 100)
background_pen = display.create_pen(50, 50, 70)
shadow_pen = display.create_pen(0, 0, 0)

while True:
    t = time.ticks_ms() / 1000.0

    if button_up.read():
        target_scroll_position -= 1
        target_scroll_position = target_scroll_position if target_scroll_position >= 0 else len(applications) - 1

    if button_down.read():
        target_scroll_position += 1
        target_scroll_position = target_scroll_position if target_scroll_position < len(applications) else 0

    if button_a.read():
        launch_application(applications[selected_item])

    display.set_pen(background_pen)
    display.clear()

    scroll_position += (target_scroll_position - scroll_position) / 5

    grid_size = 40
    for y in range(0, 240 / grid_size):
        for x in range(0, 320 / grid_size):
            h = x + y + int(t * 5)
            h = h / 50.0
            r, g, b = hsv_to_rgb(h, .5, 1)

            display.set_pen(display.create_pen(r, g, b))
            display.rectangle(x * grid_size, y * grid_size, grid_size, grid_size)

    # work out which item is selected (closest to the current scroll position)
    selected_item = round(target_scroll_position)

    start = time.ticks_ms()

    for list_index, application in enumerate(applications):
        distance = list_index - scroll_position

        text_size = 4 if selected_item == list_index else 3

        # center text horizontally
        title_width = display.measure_text(application["title"], text_size)
        text_x = int(160 - title_width / 2)

        row_height = text_size * 5 + 20

        # center list items vertically
        text_y = int(120 + distance * row_height - (row_height / 2))

        # draw the text, selected item brightest and with shadow
        if selected_item == list_index:
            text(application["title"], text_x + 1, text_y + 1, shadow_pen, text_size)

        text_pen = selected_pen if selected_item == list_index else unselected_pen
        text(application["title"], text_x, text_y, text_pen, text_size)

    start = time.ticks_ms()

    display.update()

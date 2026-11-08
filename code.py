import os
import random
import struct
import time

import board
import displayio
import microcontroller
import rtc
import terminalio

display = board.DISPLAY
scene = displayio.Group()
display.root_group = scene
font = terminalio.FONT
glyph_width, glyph_height = font.get_bounding_box()[:2]

SANTA = (
        "      RRRRR      ",
        "     RRRRRRR     ",
        "    RRRRRRRRR    ",
        "   RRRRRRRRRRR   ",
        "  wwRRRRRRRRRRR  ",
        "  ww RRRRRRRRRR  ",
        "     wwwwwwwwww  ",
        "    wwwwwwwwwwww ",
        "     ppppppppp   ",
        "    wpKpppKppw   ",
        "    wpppOpppww   ",
        "    wwwwpwwwww   ",
        "    wwwRRRwwww   ",
        "     wwwwwwww    ",
        "      wwwwww     ",
        "     RRRRRRRR    ",
        "    RRRRRRRRRR   ",
    )

# The tree is the original illustration, drawn in the same position and colours.
art = displayio.Bitmap(108, 150, 11)
colors = displayio.Palette(11)
for index, color in enumerate((
    0x000000, 0xF5FAFF, 0xF45962, 0x203546, 0xFCA75D, 0xFFD0A8,
    0x277C5C, 0x45A775, 0xFFD476, 0xD95254, 0x88614D,
)):
    colors[index] = color
colors.make_transparent(0)
hand_drawn = displayio.TileGrid(art, pixel_shader=colors)
scene.append(hand_drawn)

calendar_bitmap = displayio.OnDiskBitmap("/December-Art.bmp")
calendar_art = displayio.TileGrid(
    calendar_bitmap, pixel_shader=calendar_bitmap.pixel_shader,
    tile_width=88, tile_height=88, x=13, y=40,
)
calendar_art.hidden = True
scene.append(calendar_art)
shown_day = None


def draw_tree():
    for y in range(126, 144):
        for x in range(52, 62):
            art[x, y] = 10
    for top, height, span in ((72, 58, 46), (53, 57, 38), (36, 54, 27)):
        for dy in range(height):
            half = dy * span // height
            for dx in range(-half, half + 1):
                art[57 + dx, top + dy] = 6 if dx >= 0 else 7
    for x, y, color in ((53, 56, 8), (64, 70, 9), (44, 83, 9),
                        (69, 96, 8), (37, 112, 8), (57, 116, 9), (84, 119, 9)):
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if dx * dx + dy * dy <= 5:
                    art[x + dx, y + dy] = color
    for delta in range(-8, 9):
        art[57 + delta, 28] = 8
        art[57, 28 + delta] = 8
    for delta in range(-3, 4):
        art[57 + delta, 28 + delta] = 8
        art[57 + delta, 28 - delta] = 8


def draw_santa():
    color_index = {"w": 1, "R": 2, "K": 3, "O": 4, "p": 5}
    for row, pixels in enumerate(SANTA):
        for column, pixel in enumerate(pixels):
            if pixel != " ":
                for y in range(5):
                    for x in range(5):
                        art[14 + column * 5 + x, 43 + row * 5 + y] = color_index[pixel]


def show_art(day):
    global shown_day
    if shown_day == day:
        return
    if day in (0, 1, 25):
        art.fill(0)
        if day == 25:
            draw_santa()
        else:
            draw_tree()
        calendar_art.hidden = True
        hand_drawn.hidden = False
    else:
        # The bitmap skips the two days drawn above.
        calendar_art[0] = day - (2 if day < 25 else 3)
        hand_drawn.hidden = True
        calendar_art.hidden = False
    shown_day = day
    print("Artwork day:", day)


sky = displayio.Bitmap(320, 170, 4)
sky_colors = displayio.Palette(4)
sky_colors[0] = 0x102B3A
sky_colors[1] = 0x335D73
sky_colors[2] = 0x4A788B
sky_colors[3] = 0x294A5C
scene.insert(0, displayio.TileGrid(sky, pixel_shader=sky_colors))
random.seed(24)
for _ in range(145):
    x = random.randrange(320)
    y = random.randrange(170)
    if (x < 109 or y < 13 or y > 160) and not (13 <= x < 101 and 40 <= y < 128):
        sky[x, y] = random.randrange(1, 4)
for y in range(18, 153):
    sky[108, y] = 1
for x in range(119, 307):
    sky[x, 132] = 1
show_art(0)


class Text:
    def __init__(self, width, y, scale, color, x=119):
        group = displayio.Group(scale=scale, x=x, y=y)
        palette = displayio.Palette(2)
        palette.make_transparent(0)
        palette[1] = color
        self.tiles = displayio.TileGrid(
            font.bitmap, pixel_shader=palette, width=width, height=1,
            tile_width=glyph_width, tile_height=glyph_height,
        )
        group.append(self.tiles)
        scene.append(group)
        self.width = width
        self.last = None

    def set(self, value):
        if value == self.last:
            return
        for index, char in enumerate(value + " " * (self.width - len(value))):
            self.tiles[index] = font.get_glyph(ord(char)).tile_index
        self.last = value


title = Text(16, 19, 2, 0xFFF5DF)
days_label = Text(8, 48, 4, 0xFFD476)
clock_label = Text(8, 96, 4, 0xFFF5DF)
footer = Text(16, 143, 2, 0x9EDBC7)
title.set("CHRISTMAS EVE")
days_label.set("")
clock_label.set("--:--:--")
date_badge = Text(6, 151, 1, 0x9EDBC7, x=39)
date_badge.set("")

MIN_TIME = time.mktime((2025, 1, 1, 0, 0, 0, -1, -1, -1))
try:
    with open("/sync.txt") as sync_file:
        stamp = int(sync_file.read().strip())
    previous = struct.unpack("<I", microcontroller.nvm[:4])[0]
    if stamp != previous and 1735689600 <= stamp < 4294967296:
        rtc.RTC().datetime = time.localtime(stamp)
        microcontroller.nvm[:4] = struct.pack("<I", stamp)
except (OSError, ValueError):
    pass

ssid = os.getenv("CLOCK_WIFI_SSID")
footer.set("SYNCING WIFI" if ssid else "USB SYNC NEEDED")
ntp = None
next_sync = 0
last = None
last_report = -1
while True:
    now = time.time()
    if now != last:
        last = now
        if now >= MIN_TIME:
            date = time.localtime(now)
            day = date.tm_mday if date.tm_mon == 12 else 0
            show_art(day)
            date_badge.set("{:02} DEC".format(day) if day else "")
            year = date.tm_year
            christmas = time.mktime((year, 12, 25, 0, 0, 0, -1, -1, -1))
            if christmas <= now < christmas + 86400:
                title.set("MERRY CHRISTMAS!")
                days_label.set("")
                clock_label.set("HO HO HO")
                footer.set("25 DEC")
            else:
                if now > christmas:
                    year += 1
                    christmas = time.mktime((year, 12, 25, 0, 0, 0, -1, -1, -1))
                days, remainder = divmod(christmas - now, 86400)
                hours, remainder = divmod(remainder, 3600)
                minutes, seconds = divmod(remainder, 60)
                title.set("CHRISTMAS EVE")
                days_label.set("{} {}".format(days, "DAY" if days == 1 else "DAYS"))
                clock_label.set("{:02}:{:02}:{:02}".format(hours, minutes, seconds))
                footer.set("24 DEC MIDNIGHT")
            if now != last_report:
                print(title.last, days_label.last, clock_label.last, footer.last)
                last_report = now

    if ssid and time.monotonic() >= next_sync:
        clock_unset = now < MIN_TIME
        if clock_unset:
            footer.set("SYNCING WIFI")
        try:
            import adafruit_ntp
            import socketpool
            import wifi
            if not wifi.radio.connected:
                wifi.radio.connect(ssid, os.getenv("CLOCK_WIFI_PASSWORD", ""), timeout=6)
            if ntp is None:
                ntp = adafruit_ntp.NTP(socketpool.SocketPool(wifi.radio))
            network_time = ntp.datetime
            if network_time.tm_year < 2025:
                raise ValueError("NTP returned an invalid date")
            rtc.RTC().datetime = network_time
            last = None
            print("Network time synced")
            next_sync = time.monotonic() + 3600
        except (OSError, RuntimeError, ValueError, ArithmeticError, ImportError) as error:
            print("Network time:", error)
            if clock_unset:
                footer.set("WIFI RETRYING")
            next_sync = time.monotonic() + (15 if clock_unset else 60)
    time.sleep(0.12)

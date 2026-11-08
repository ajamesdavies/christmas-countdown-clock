# Christmas Countdown Clock

An Advent-style countdown for the LILYGO T-Display S3. The built-in display
counts down to midnight UK time at the end of Christmas Eve, with a
different illustration for every December date. Santa appears on Christmas
Day, and the countdown starts again on 26 December.

## Install

1. Install [CircuitPython for the LILYGO T-Display S3](https://circuitpython.org/board/lilygo_tdisplay_s3/).
   This project was tested with CircuitPython 10.3.1.
2. Connect the board with a USB data cable. Copy `code.py`, `December-Art.bmp`
   and the `lib` folder to its `CIRCUITPY` drive.
3. Set the time using one of the options below.

## Set the time

For automatic sync after a power cut, add your own 2.4 GHz network details
to `settings.toml` on the board and press RESET:

```toml
CLOCK_WIFI_SSID = "your 2.4 GHz Wi-Fi name"
CLOCK_WIFI_PASSWORD = "your Wi-Fi password"
```

On Windows, you can also run the setup script with the board plugged in:

```powershell
.\Sync-Clock.ps1 -ConfigureWifi
```

For a one-time USB sync without Wi-Fi, run `.\Sync-Clock.ps1`. Repeat after
a complete loss of power if the board has no Wi-Fi time source.

## Credits

- The 29 illustrations in `December-Art.bmp` are resized and composited
  [Twemoji v16.0.1](https://github.com/jdecked/twemoji/tree/v16.0.1) graphics
  by Twitter, Inc., the Twemoji contributors and the jdecked fork contributors,
  under [CC BY 4.0](licenses/twemoji-CC-BY-4.0.txt).
- `lib/adafruit_ntp.py` is the
  [Adafruit CircuitPython NTP library](https://github.com/adafruit/Adafruit_CircuitPython_NTP)
  by Scott Shawcroft for Adafruit Industries, under the
  [MIT license](licenses/adafruit-ntp-MIT.txt).

import Adafruit_ILI9341 as TFT
from gpiozero import DigitalOutputDevice
import spidev
from PIL import Image, ImageDraw

# تنظیمات پین‌ها
DC_PIN = 24  # GPIO 24
RST_PIN = 25  # GPIO 25
SPI_PORT = 0
SPI_DEVICE = 0  # برای spidev0.0، اگه spidev0.1 بود به 1 تغییر بده

# راه‌اندازی پین‌ها با gpiozero
dc = DigitalOutputDevice(DC_PIN)
rst = DigitalOutputDevice(RST_PIN)

# راه‌اندازی SPI
spi = spidev.SpiDev()
spi.open(SPI_PORT, SPI_DEVICE)
spi.max_speed_hz = 64000000

# راه‌اندازی LCD
disp = TFT.ILI9341(dc=dc, rst=rst, spi=spi)
disp.begin()

# ایجاد تصویر تست
image = Image.new("RGB", (320, 240), "black")
draw = ImageDraw.Draw(image)
draw.text((30, 40), "GPIOZero Test", fill="white")
disp.display(image)

print("نمایش روی LCD انجام شد!")

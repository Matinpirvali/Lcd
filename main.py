from gpiozero import DigitalOutputDevice
import spidev
import time
from PIL import Image

# تنظیم پایه‌ها (براساس پین‌بندی شما)
CS = DigitalOutputDevice(22)    # Chip Select
DC = DigitalOutputDevice(17)    # Data/Command
RST = DigitalOutputDevice(27)   # Reset

# مقداردهی اولیه SPI
spi = spidev.SpiDev(0, 0)
spi.max_speed_hz = 40000000  

# دستورات ILI9341
ILI9341_SWRESET = 0x01
ILI9341_SLPOUT  = 0x11
ILI9341_DISPON  = 0x29
ILI9341_CASET   = 0x2A
ILI9341_PASET   = 0x2B
ILI9341_RAMWR   = 0x2C

# ابعاد نمایشگر (براساس مدل شما ممکن است متفاوت باشد)
WIDTH = 240
HEIGHT = 320

def send_command(cmd):
    DC.off()        # دستور
    CS.off()
    spi.writebytes([cmd])
    CS.on()

def send_data(data):
    DC.on()         # داده
    CS.off()
    if isinstance(data, int):
        spi.writebytes([data])
    else:
        spi.writebytes(data)
    CS.on()

def init_display():
    # ریست اولیه نمایشگر
    RST.off()
    time.sleep(0.1)
    RST.on()
    time.sleep(0.1)
    
    send_command(ILI9341_SWRESET)
    time.sleep(0.1)
    send_command(ILI9341_SLPOUT)
    time.sleep(0.1)
    send_command(ILI9341_DISPON)

def set_address_window(x0, y0, x1, y1):
    # تنظیم محدوده X
    send_command(ILI9341_CASET)
    send_data([0x00, x0, 0x00, x1])
    
    # تنظیم محدوده Y
    send_command(ILI9341_PASET)
    send_data([0x00, y0, 0x00, y1])
    
    # آماده‌سازی برای نوشتن به RAM
    send_command(ILI9341_RAMWR)

def convert_image_to_rgb565(image_path):
    """
    تصویر ورودی را به اندازه نمایشگر تغییر اندازه داده و به فرمت RGB565 تبدیل می‌کند.
    """
    img = Image.open(image_path)
    img = img.resize((WIDTH, HEIGHT))  # تغییر اندازه به ابعاد نمایشگر
    img = img.convert('RGB')             # تبدیل به RGB در صورت نیاز

    pixel_data = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b = img.getpixel((x, y))
            # تبدیل به فرمت RGB565
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            # تقسیم داده به دو بایت (بیت‌های بالا و پایین)
            pixel_data.append(rgb565 >> 8)    # بایت بالا
            pixel_data.append(rgb565 & 0xFF)    # بایت پایین
    return pixel_data

def display_image(image_path):
    set_address_window(0, 0, WIDTH - 1, HEIGHT - 1)
    image_data = convert_image_to_rgb565(image_path)
    send_data(image_data)

# اجرای برنامه
init_display()
display_image("simple_image.jpg")  # جایگزین کردن نام تصویر موردنظر

print("تصویر ساده نمایش داده شد!")

# حلقه بی‌نهایت برای جلوگیری از خاتمه برنامه
while True:
    time.sleep(1)

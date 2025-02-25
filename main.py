from gpiozero import DigitalOutputDevice
import spidev
import time
from PIL import Image

# پین‌های مربوط به نمایشگر (براساس سیم‌کشی خودتان اصلاح کنید)
CS  = DigitalOutputDevice(22)  # Chip Select
DC  = DigitalOutputDevice(17)  # Data/Command
RST = DigitalOutputDevice(27)  # Reset

# راه‌اندازی اولیه SPI
spi = spidev.SpiDev(0, 0)
spi.max_speed_hz = 40000000  
# اگر لازم شد مد SPI را هم مشخص کنید (بعضی ماژول‌ها به مد 0 یا 3 نیاز دارند)
# spi.mode = 0

# دستورات ILI9341
ILI9341_SWRESET = 0x01
ILI9341_SLPOUT  = 0x11
ILI9341_DISPON  = 0x29
ILI9341_CASET   = 0x2A
ILI9341_PASET   = 0x2B
ILI9341_RAMWR   = 0x2C

# ابعاد نمایشگر (بسیاری از ماژول‌های 2.4 یا 2.8 اینچی 240x320 هستند)
WIDTH = 240
HEIGHT = 320

def send_command(cmd):
    DC.off()  # حالت دستور
    CS.off()
    spi.writebytes([cmd])
    CS.on()

def send_data(data):
    DC.on()   # حالت داده
    CS.off()
    # اگر آرگومان یک عدد باشد
    if isinstance(data, int):
        spi.writebytes([data])
    else:
        # برای جلوگیری از ارور در صورت زیاد بودن حجم داده، آن را در بسته‌های کوچک ارسال می‌کنیم
        chunk_size = 4096
        for i in range(0, len(data), chunk_size):
            spi.writebytes(data[i:i+chunk_size])
    CS.on()

def init_display():
    """
    مقداردهی اولیه کامل برای اکثر ماژول‌های ILI9341.
    اگر باز هم تصویر به‌هم‌ریخته بود، احتمال دارد درایور متفاوت باشد
    یا لازم باشد بعضی مقادیر این رجیسترها تغییر کند.
    """
    # ریست سخت‌افزاری
    RST.off()
    time.sleep(0.1)
    RST.on()
    time.sleep(0.1)

    # ریست نرم‌افزاری
    send_command(ILI9341_SWRESET)
    time.sleep(0.12)

    # Power Control A
    send_command(0xCB)
    send_data([0x39, 0x2C, 0x00, 0x34, 0x02])

    # Power Control B
    send_command(0xCF)
    send_data([0x00, 0xC1, 0x30])

    # Driver timing control A
    send_command(0xE8)
    send_data([0x85, 0x00, 0x78])

    # Driver timing control B
    send_command(0xEA)
    send_data([0x00, 0x00])

    # Power on sequence control
    send_command(0xED)
    send_data([0x64, 0x03, 0x12, 0x81])

    # Pump ratio control
    send_command(0xF7)
    send_data([0x20])

    # Power Control 1
    send_command(0xC0)
    send_data([0x23])

    # Power Control 2
    send_command(0xC1)
    send_data([0x10])

    # VCOM Control 1
    send_command(0xC5)
    send_data([0x3E, 0x28])

    # VCOM Control 2
    send_command(0xC7)
    send_data([0x86])

    # Memory Access Control (جهت نمایش)
    # 0x48 یا 0x28 یا مقادیر دیگر ممکن است بسته به جهت دلخواه تغییر کند
    send_command(0x36)
    send_data([0x48])  

    # Pixel Format Set (تنظیم 16 بیت برای هر پیکسل)
    send_command(0x3A)
    send_data([0x55])  # 16bit

    # Frame Rate Control
    send_command(0xB1)
    send_data([0x00, 0x18])

    # Display Function Control
    send_command(0xB6)
    send_data([0x08, 0x82, 0x27])

    # 3Gamma Function Disable
    send_command(0xF2)
    send_data([0x00])

    # Gamma Curve Selected
    send_command(0x26)
    send_data([0x01])

    # Positive Gamma Correction
    send_command(0xE0)
    send_data([
        0x0F, 0x31, 0x2B, 0x0C, 0x0E, 0x08, 0x4E, 0xF1, 
        0x37, 0x07, 0x10, 0x03, 0x0E, 0x09, 0x00
    ])

    # Negative Gamma Correction
    send_command(0xE1)
    send_data([
        0x00, 0x0E, 0x14, 0x03, 0x11, 0x07, 0x31, 0xC1,
        0x48, 0x08, 0x0F, 0x0C, 0x31, 0x36, 0x0F
    ])

    # از حالت Sleep خارج شو
    send_command(ILI9341_SLPOUT)
    time.sleep(0.12)

    # روشن کردن نمایشگر
    send_command(ILI9341_DISPON)
    time.sleep(0.12)

def set_address_window(x0, y0, x1, y1):
    send_command(ILI9341_CASET)
    send_data([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF])

    send_command(ILI9341_PASET)
    send_data([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF])

    send_command(ILI9341_RAMWR)

def convert_image_to_rgb565(image_path):
    """
    تصویر را به اندازه نمایشگر تغییر داده و به فرمت 16بیتی (RGB565) تبدیل می‌کند.
    """
    img = Image.open(image_path)
    img = img.resize((WIDTH, HEIGHT))
    img = img.convert('RGB')

    pixel_data = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b = img.getpixel((x, y))
            # تبدیل به RGB565: 5 بیت قرمز، 6 بیت سبز، 5 بیت آبی
            rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            pixel_data.append(rgb565 >> 8)      # بایت بالایی
            pixel_data.append(rgb565 & 0xFF)    # بایت پایینی
    return pixel_data

def display_image(image_path):
    """
    با تنظیم محدوده‌ی کل صفحه و ارسال داده‌های پیکسلی، تصویر را نمایش می‌دهد.
    """
    set_address_window(0, 0, WIDTH - 1, HEIGHT - 1)
    image_data = convert_image_to_rgb565(image_path)
    send_data(image_data)

# --- اجرای اصلی برنامه ---
init_display()               # مقداردهی اولیه کامل
display_image("IMG_20250224_171236.jpg")  # تصویر خود را اینجا بگذارید

print("تصویر نمایش داده شد!")

while True:
    time.sleep(1)

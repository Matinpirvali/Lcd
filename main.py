from gpiozero import DigitalOutputDevice
import spidev
import time
from PIL import Image

# تنظیم پایه‌ها
CS = DigitalOutputDevice(17)    # Chip Select (GPIO17، به‌جای GPIO8)
DC = DigitalOutputDevice(17)    # Data/Command (GPIO17، پین عمومی آزاد)
RST = DigitalOutputDevice(27)   # Reset (GPIO27، پین عمومی آزاد)

# مقداردهی اولیه SPI
spi = spidev.SpiDev(0, 0)
spi.max_speed_hz = 40000000  # سرعت حداکثری 40 مگاهرتز

# دستورات ILI9341
ILI9341_SWRESET = 0x01
ILI9341_SLPOUT  = 0x11
ILI9341_DISPON  = 0x29
ILI9341_CASET   = 0x2A
ILI9341_PASET   = 0x2B
ILI9341_RAMWR   = 0x2C

def send_command(cmd):
    try:
        DC.off()  # حالت Command (پایین)
        CS.off()  # فعال کردن چیپ
        spi.writebytes([cmd])
        CS.on()   # غیرفعال کردن چیپ
    except Exception as e:
        print(f"خطا در send_command: {e}")

def send_data(data):
    try:
        DC.on()   # حالت Data (بالا)
        CS.off()  # فعال کردن چیپ
        spi.writebytes([data] if isinstance(data, int) else data)
        CS.on()   # غیرفعال کردن چیپ
    except Exception as e:
        print(f"خطا در send_data: {e}")

def init_display():
    try:
        RST.off()
        time.sleep(0.1)
        RST.on()
        time.sleep(0.1)

        send_command(ILI9341_SWRESET)  # ریست نرم‌افزاری
        time.sleep(0.1)
        send_command(ILI9341_SLPOUT)   # خروج از حالت خواب
        time.sleep(0.1)
        send_command(ILI9341_DISPON)   # روشن کردن نمایشگر
    except Exception as e:
        print(f"خطا در init_display: {e}")

def display_image(image_path="IMG_20250224_113036.jpg"):
    try:
        # باز کردن و پردازش تصویر
        img = Image.open(image_path).convert("RGB")  # تبدیل به فرمت RGB
        img = img.resize((240, 320))  # تغییر اندازه به 240x320 پیکسل
        pixels = list(img.getdata())

        # تنظیم محدوده X (کل عرض 240 پیکسل)
        send_command(ILI9341_CASET)
        send_data([0x00, 0x00, 0x00, 0xEF])  # X از 0 تا 239

        # تنظیم محدوده Y (کل ارتفاع 320 پیکسل)
        send_command(ILI9341_PASET)
        send_data([0x00, 0x00, 0x01, 0x3F])  # Y از 0 تا 319

        # شروع نوشتن داده‌ها در حافظه نمایشگر
        send_command(ILI9341_RAMWR)

        # تبدیل پیکسل‌ها به فرمت 16 بیتی RGB (5-6-5)
        image_data = []
        for r, g, b in pixels:
            # تبدیل به فرمت 16 بیتی (5 بیت قرمز، 6 بیت سبز، 5 بیت آبی)
            r_16 = (r & 0xF8) << 8  # 5 بیت قرمز
            g_16 = (g & 0xFC) << 3  # 6 بیت سبز
            b_16 = (b & 0xF8) >> 3  # 5 بیت آبی
            pixel = r_16 | g_16 | b_16
            image_data.extend([pixel >> 8, pixel & 0xFF])  # دو بایت برای هر پیکسل

        # ارسال داده‌ها به‌صورت تکه‌تکه (چون بیش از 4096 بایت هست)
        chunk_size = 2048  # اندازه هر تکه (کمتر از 4096 بایت)
        for i in range(0, len(image_data), chunk_size):
            chunk = image_data[i:i + chunk_size]
            send_data(chunk)
    except Exception as e:
        print(f"خطا در display_image: {e}")

# اجرای برنامه
if name == "__main__":
    try:
        init_display()
        display_image()  # فرض می‌کنه فایل image.png در دایرکتوری فعلی هست
        print("تصویر روی صفحه نمایش نشان داده شد!")
    except Exception as e:
        print(f"خطا در اجرای برنامه: {e}")

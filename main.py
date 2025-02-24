from gpiozero import DigitalOutputDevice
import spidev
import time

# تنظیم پایه‌ها
CS = DigitalOutputDevice(22)    # Chip Select (GPIO17، به‌جای GPIO8)
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

def display_image():
    try:
        # تنظیم محدوده X (کل عرض 240 پیکسل)
        send_command(ILI9341_CASET)
        send_data([0x00, 0x00, 0x00, 0xEF])  # X از 0 تا 239

        # تنظیم محدوده Y (کل ارتفاع 320 پیکسل)
        send_command(ILI9341_PASET)
        send_data([0x00, 0x00, 0x01, 0x3F])  # Y از 0 تا 319

        # شروع نوشتن داده‌ها در حافظه نمایشگر
        send_command(ILI9341_RAMWR)

        # ایجاد الگوی تصویر (نوارهای رنگی عمودی به‌عنوان مثال)
        image_data = []
        for y in range(320):  # ارتفاع 320 پیکسل
            for x in range(240):  # عرض 240 پیکسل
                # الگوی ساده: نوارهای رنگی عمودی
                if x < 80:  # نوار قرمز (0xF800)
                    r, g, b = 0xF8, 0x00, 0x00
                elif x < 160:  # نوار سبز (0x07E0)
                    r, g, b = 0x00, 0x7E, 0x00
                else:  # نوار آبی (0x001F)
                    r, g, b = 0x00, 0x00, 0x1F
                # ترکیب رنگ‌ها در فرمت 16 بیتی RGB (5-6-5)
                pixel = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                image_data.extend([pixel >> 8, pixel & 0xFF])  # دو بایت برای هر پیکسل

        # ارسال داده‌ها به‌صورت تکه‌تکه (چون بیش از 4096 بایت هست)
        chunk_size = 2048  # اندازه هر تکه (کمتر از 4096 بایت)
        for i in range(0, len(image_data), chunk_size):
            chunk = image_data[i:i + chunk_size]
            send_data(chunk)
    except Exception as e:
        print(f"خطا در display_image: {e}")

# اجرای برنامه
    try:
        init_display()
        display_image()
        print("تصویر روی صفحه نمایش نشان داده شد!")
    except Exception as e:
        print(f"خطا در اجرای برنامه: {e}")
while:

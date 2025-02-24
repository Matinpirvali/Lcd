from gpiozero import DigitalOutputDevice
import spidev
import time

# تنظیم پایه‌های GPIO
CS = DigitalOutputDevice(22)   # Chip Select
DC = DigitalOutputDevice(17)   # Data/Command
RST = DigitalOutputDevice(27)  # Reset

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

def send_command(cmd):
    DC.off()
    CS.off()
    spi.writebytes([cmd])
    CS.on()

def send_data(data):
    DC.on()
    CS.off()
    spi.writebytes(data)
    CS.on()

def init_display():
    RST.off()
    time.sleep(0.1)
    RST.on()
    time.sleep(0.1)

    send_command(ILI9341_SWRESET)
    time.sleep(0.1)
    send_command(ILI9341_SLPOUT)
    time.sleep(0.1)
    send_command(ILI9341_DISPON)

def display_image(image_path):
    send_command(ILI9341_CASET)
    send_data([0x00, 0x00, 0x00, 0xEF])  # محدوده X (240 پیکسل)
    
    send_command(ILI9341_PASET)
    send_data([0x00, 0x00, 0x01, 0x3F])  # محدوده Y (320 پیکسل)

    send_command(ILI9341_RAMWR)

    # خواندن فایل RGB565 و ارسال به نمایشگر
    with open(image_path, "rb") as f:
        while chunk := f.read(4096):  # ارسال به صورت بلوک‌های ۴ کیلوبایتی
            send_data(list(chunk))

# اجرای برنامه
init_display()
display_image("sample_image.rgb")  # فایل تصویر را اینجا وارد کن

print("تصویر روی نمایشگر ارسال شد!")

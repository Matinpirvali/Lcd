from gpiozero import DigitalOutputDevice
import spidev
import time

# تنظیم پایه‌ها
CS = DigitalOutputDevice(8)   # Chip Select (GPIO8)
DC = DigitalOutputDevice(24)  # Data/Command (GPIO24)
RST = DigitalOutputDevice(25) # Reset (GPIO25)

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
    spi.writebytes([data] if isinstance(data, int) else data)
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

def clear_screen():
    send_command(ILI9341_CASET)
    send_data([0x00, 0x00, 0x00, 0xEF]) # تنظیم محدوده X

    send_command(ILI9341_PASET)
    send_data([0x00, 0x00, 0x01, 0x3F]) # تنظیم محدوده Y

    send_command(ILI9341_RAMWR)
    
    black_color = [0x00, 0x00] * (240 * 320)  # مقداردهی به رنگ مشکی
    send_data(black_color)

# اجرای برنامه
init_display()
clear_screen()
print("صفحه نمایش سیاه شد!")

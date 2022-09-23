import RPi.GPIO as GPIO
import time
import datetime
import I2C_LCD_driver
import os

# GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

botaoDesligar = 18
GPIO.setup(botaoDesligar, GPIO.IN, pull_up_down=GPIO.PUD_UP)
lcdi2c = I2C_LCD_driver.lcd()

if (GPIO.input(botaoDesligar) == False):
    lcdi2c.lcd_clear()
    lcdi2c.lcd_display_string("Pressione novamente para desligar", 1, 0)
    time.sleep(1)

    if (GPIO.input(botaoDesligar) == False):
        lcdi2c.lcd_clear()
        lcdi2c.lcd_display_string("Desligando...", 1, 0)
        time.sleep(1)
        lcdi2c.backlight(0)
        os.system("sudo shutdown now")
#!/usr/bin/python

import smbus
import time
import subprocess
import socket
import datetime
import string

# Define some device parameters
I2C_ADDR  = 0x27 # I2C device address, if any error, change this address to 0x27
LCD_WIDTH = 16   # Maximum characters per line

# Define some device constants
LCD_CHR = 1 # Mode - Sending data
LCD_CMD = 0 # Mode - Sending command

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

LCD_BACKLIGHT  = 0x08  # On
#LCD_BACKLIGHT = 0x00  # Off

ENABLE = 0b00000100 # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

#Open I2C interface
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1

def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)



def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = the data
  # mode = 1 for data
  #        0 for command

  bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
  bits_low = mode | ((bits<<4) & 0xF0) | LCD_BACKLIGHT

  # High bits
  bus.write_byte(I2C_ADDR, bits_high)
  lcd_toggle_enable(bits_high)

  # Low bits
  bus.write_byte(I2C_ADDR, bits_low)
  lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
  # Toggle enable
  time.sleep(E_DELAY)
  bus.write_byte(I2C_ADDR, (bits | ENABLE))
  time.sleep(E_PULSE)
  bus.write_byte(I2C_ADDR,(bits & ~ENABLE))
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

def is_connected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
#	print(" We will try now")
        socket.create_connection(("www.google.com", 80))
        return True
    except:
#        pass
#	print("we have an error now what")
        return False

def main():
  # Main program block

  # Initialise display
  lcd_init()

  lcd_string(" Cello Systems ",LCD_LINE_1)
  lcd_string(" Loading ...... ",LCD_LINE_2)

  Internet = 1
   
  while Internet:
      if is_connected():
        #  print("Internet connection validated")
        #  log.debug('Cello - Internet connection validated')
          Internet = 0                      # get out of the loop we have a connection
      else:
         # print("no connection- try again")
         # log.debug('Cello - No Internet connection- try again')
          time.sleep(3)			    # wait ti try again
          
  
  # check for Internet connection if we have one all good if not wait and tell user what is happening

  while True:

    # Send some test
    lcd_string(" Cello Systems ",LCD_LINE_1)
    lcd_string(" CelloConf TV  ",LCD_LINE_2)

    time.sleep(3)
  
    cmd = "hostname -I | cut -d\' \' -f1" 
    IP = format(subprocess.check_output(cmd, shell = True ).decode("utf-8").strip())

    # Send some more text
    lcd_string(str(IP),LCD_LINE_1)
    lcd_string("http://ip:8000",LCD_LINE_2)

    time.sleep(3)

    # Send some more info
    x = datetime.datetime.now()
    lcd_string(x.strftime(" %d/%m/%Y"),LCD_LINE_1)
    lcd_string(x.strftime(" %H:%M"),LCD_LINE_2)

    time.sleep(3)
if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)


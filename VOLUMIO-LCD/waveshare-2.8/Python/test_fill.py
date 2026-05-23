import time
from PIL import Image
import LCD_2inch8

disp = LCD_2inch8.LCD_2inch8()
disp.ST7789_Init()
disp.clear()

for color in ["red", "green", "blue", "black", "white"]:
    img = Image.new("RGB", (disp.width, disp.height), color)
    disp.ShowImage(img)
    time.sleep(2)

disp.LCD_module_exit()

#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import chardet
import os
import sys 
import time
import logging
import LCD_2inch8,Touch_2inch8
from Touch_2inch8 import touch_data,Touch_Data_Old
from PIL import Image,ImageDraw,ImageFont

logging.basicConfig(level=logging.DEBUG)
global Flag


try:
    ''' Warning!!!Don't  creation of multiple displayer objects!!! '''
    touch = Touch_2inch8.Touch_2inch8()
    touch.CST328_init()
    disp = LCD_2inch8.LCD_2inch8()
    # Initialize library.
    disp.ST7789_Init()
    # Clear display.
    disp.clear()


    logging.info("show image")
    ImagePath = ["./pic/LCD_2inch8_1.jpg", "./pic/LCD_2inch8_2.jpg", "./pic/LCD_2inch8_3.jpg"]
    for i in range(0, 3):
        image = Image.open(ImagePath[i])	
        # image = image.rotate(0)
        disp.ShowImage(image)
        time.sleep(2)
    
    
    
    # 画板示例
    Canvas = Image.new("RGB", (disp.width, disp.height), "RED")
    draw = ImageDraw.Draw(Canvas)
    disp.ShowImage(Canvas)
                    
    Start_Flag = 0
    while True:      
        if touch_data.state :
            touch_data.state  = 0 
            if(touch_data.points > 1):
                for i in range(touch_data.points):
                    draw.rectangle(((touch_data.coords[i]["x"], (touch_data.coords[i]["y"]),touch_data.coords[i]["x"]+35,touch_data.coords[i]["y"]+35)), fill="blue", outline="red", width=2)
                    Touch_Data_Old.points = touch_data.points
                disp.ShowImage(Canvas)
            else:
                if(Touch_Data_Old.points > 1) :
                    disp.ShowImage(Canvas)
                if(Start_Flag == 0):
                    Start_Flag = 1
                    Touch_Data_Old.x = touch_data.coords[0]["x"]
                    Touch_Data_Old.y = touch_data.coords[0]["y"]
                else:
                    #print("Landscape screen Xstart="+str(Touch_Data_Old.x)+"Ystart="+str(Touch_Data_Old.y)+"Xend="+str(touch_data.coords[0]["x"])+"Yend="+str(touch_data.coords[0]["y"]))
                    draw.line(((Touch_Data_Old.x, Touch_Data_Old.y),( touch_data.coords[0]["x"], touch_data.coords[0]["y"])),fill=None, width=2)
                    disp.ShowImage_Windows(Touch_Data_Old.x,Touch_Data_Old.y,touch_data.coords[0]["x"], touch_data.coords[0]["y"],Canvas)
                    Touch_Data_Old.x = touch_data.coords[0]["x"]
                    Touch_Data_Old.y = touch_data.coords[0]["y"]
                    Touch_Data_Old.points = touch_data.points
                    touch_data.points = 0
        elif(touch_data.state == 0 and touch_data.points > 1):
            touch_data.points = 0
            Touch_Data_Old.points = 0
            Canvas = Image.new("RGB", (disp.width, disp.height), "RED")
            draw = ImageDraw.Draw(Canvas)
            disp.ShowImage(Canvas)
   
except IOError as e:
    logging.info(e)    
except KeyboardInterrupt:
    disp.LCD_module_exit()
    logging.info("quit:")
    exit()

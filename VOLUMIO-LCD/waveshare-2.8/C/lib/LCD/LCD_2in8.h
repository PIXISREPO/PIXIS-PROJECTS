/*****************************************************************************
* | File      	:   LCD_2IN8.h
* | Author      :   Waveshare team
* | Function    :   Hardware underlying interface
* | Info        :
*                Used to shield the underlying layers of each master 
*                and enhance portability
*----------------
* |	This version:   V1.0
* | Date        :   2020-12-16
* | Info        :   Basic version
*
******************************************************************************/
#ifndef __LCD_2IN8_H
#define __LCD_2IN8_H	
	
#include "DEV_Config.h"
#include <stdint.h>

#include <stdlib.h>		//itoa()
#include <stdio.h>


#define LCD_2IN8_WIDTH 240
#define LCD_2IN8_HEIGHT 320


#define HORIZONTAL 0
#define VERTICAL   1

#define LCD_2IN8_SetBacklight(Value) DEV_SetBacklight(Value) 

#define LCD_2IN8_CS_0	LCD_CS_0	 
#define LCD_2IN8_CS_1	LCD_CS_1	
	                 
#define LCD_2IN8_RST_0	LCD_RST_0	
#define LCD_2IN8_RST_1	LCD_RST_1	
	                  
#define LCD_2IN8_DC_0	LCD_DC_0	
#define LCD_2IN8_DC_1	LCD_DC_1	
	                  
#define LCD_2IN8_BL_0	LCD_BL_0	
#define LCD_2IN8_BL_1	LCD_BL_1	

typedef struct{
	UWORD WIDTH;
	UWORD HEIGHT;
	UBYTE SCAN_DIR;
}LCD_2IN8_ATTRIBUTES;
extern LCD_2IN8_ATTRIBUTES LCD_2IN8;

/********************************************************************************
function:	
			Macro definition variable name
********************************************************************************/
void LCD_2IN8_Init(UBYTE Scan_dir);
void LCD_2IN8_Clear(UWORD Color);
void LCD_2IN8_Display(UWORD *Image);
void LCD_2IN8_DisplayWindows(UWORD Xstart, UWORD Ystart, UWORD Xend, UWORD Yend, UWORD *Image);
void LCD_2IN8_DisplayPoint(UWORD X, UWORD Y, UWORD Color);
void Handler_2IN8_LCD(int signo);
#endif

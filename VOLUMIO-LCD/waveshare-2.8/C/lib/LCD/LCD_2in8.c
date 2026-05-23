/*****************************************************************************
* | File      	:   LCD_2IN8.c
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
#include "LCD_2in8.h"
#include "DEV_Config.h"

#include <stdlib.h>		//itoa()
#include <stdio.h>

LCD_2IN8_ATTRIBUTES LCD_2IN8;


/******************************************************************************
function :	Hardware reset
parameter:
******************************************************************************/
static void LCD_2IN8_Reset(void)
{
    LCD_2IN8_RST_1;
    DEV_Delay_ms(100);
    LCD_2IN8_RST_0;
    DEV_Delay_ms(100);
    LCD_2IN8_RST_1;
    DEV_Delay_ms(100);
}

/******************************************************************************
function :	send command
parameter:
     Reg : Command register
******************************************************************************/
static void LCD_2IN8_SendCommand(UBYTE Reg)
{
    LCD_2IN8_DC_0;
    //LCD_2IN8_CS_0;
    DEV_SPI_WriteByte(Reg);
    //LCD_2IN8_CS_1;
}

/******************************************************************************
function :	send data
parameter:
    Data : Write data
******************************************************************************/
static void LCD_2IN8_SendData_8Bit(UBYTE Data)
{
    LCD_2IN8_DC_1;
    //LCD_2IN8_CS_0;
    DEV_SPI_WriteByte(Data);
    //LCD_2IN8_CS_1;
}

/******************************************************************************
function :	send data
parameter:
    Data : Write data
******************************************************************************/
static void LCD_2IN8_SendData_16Bit(UWORD Data)
{
    LCD_2IN8_DC_1;
    //LCD_2IN8_CS_0;
    DEV_SPI_WriteByte(Data >> 8);
    DEV_SPI_WriteByte(Data);
    //LCD_2IN8_CS_1;
	
}

/******************************************************************************
function :	Initialize the lcd register
parameter:
******************************************************************************/
static void LCD_2IN8_InitReg(void)
{
    LCD_2IN8_Reset();
	
    LCD_2IN8_SendCommand(0x36);
    LCD_2IN8_SendData_8Bit(0x00);

    LCD_2IN8_SendCommand(0x3A);
    LCD_2IN8_SendData_8Bit(0x05);

    LCD_2IN8_SendCommand(0xB2);
    LCD_2IN8_SendData_8Bit(0x0B);
    LCD_2IN8_SendData_8Bit(0x0B);
    LCD_2IN8_SendData_8Bit(0x00);
    LCD_2IN8_SendData_8Bit(0x33);
    LCD_2IN8_SendData_8Bit(0x35);

    LCD_2IN8_SendCommand(0xB7);
    LCD_2IN8_SendData_8Bit(0x11);

    LCD_2IN8_SendCommand(0xBB);
    LCD_2IN8_SendData_8Bit(0x35);

    LCD_2IN8_SendCommand(0xC0);
    LCD_2IN8_SendData_8Bit(0x2C);

    LCD_2IN8_SendCommand(0xC2);
    LCD_2IN8_SendData_8Bit(0x01);

    LCD_2IN8_SendCommand(0xC3);
    LCD_2IN8_SendData_8Bit(0x0D);

    LCD_2IN8_SendCommand(0xC4);
    LCD_2IN8_SendData_8Bit(0x20);

    LCD_2IN8_SendCommand(0xC6);
    LCD_2IN8_SendData_8Bit(0x13);

    LCD_2IN8_SendCommand(0xD0);
    LCD_2IN8_SendData_8Bit(0xA4);
    LCD_2IN8_SendData_8Bit(0xA1);

    LCD_2IN8_SendCommand(0xD6);
    LCD_2IN8_SendData_8Bit(0xA1);

    LCD_2IN8_SendCommand(0xE0);
    LCD_2IN8_SendData_8Bit(0xF0);
    LCD_2IN8_SendData_8Bit(0x06);
    LCD_2IN8_SendData_8Bit(0x0B);
    LCD_2IN8_SendData_8Bit(0x0A);
    LCD_2IN8_SendData_8Bit(0x09);
    LCD_2IN8_SendData_8Bit(0x26);
    LCD_2IN8_SendData_8Bit(0x29);
    LCD_2IN8_SendData_8Bit(0x33);
    LCD_2IN8_SendData_8Bit(0x41);
    LCD_2IN8_SendData_8Bit(0x18);
    LCD_2IN8_SendData_8Bit(0x16);
    LCD_2IN8_SendData_8Bit(0x15);
    LCD_2IN8_SendData_8Bit(0x29);
    LCD_2IN8_SendData_8Bit(0x2D);

    LCD_2IN8_SendCommand(0xE1);
    LCD_2IN8_SendData_8Bit(0xF0);
    LCD_2IN8_SendData_8Bit(0x04);
    LCD_2IN8_SendData_8Bit(0x08);
    LCD_2IN8_SendData_8Bit(0x08);
    LCD_2IN8_SendData_8Bit(0x07);
    LCD_2IN8_SendData_8Bit(0x03);
    LCD_2IN8_SendData_8Bit(0x28);
    LCD_2IN8_SendData_8Bit(0x32);
    LCD_2IN8_SendData_8Bit(0x40);
    LCD_2IN8_SendData_8Bit(0x3B);
    LCD_2IN8_SendData_8Bit(0x19);
    LCD_2IN8_SendData_8Bit(0x18);
    LCD_2IN8_SendData_8Bit(0x2A);
    LCD_2IN8_SendData_8Bit(0x2E);

    LCD_2IN8_SendCommand(0x21);

    LCD_2IN8_SendCommand(0x11);
    DEV_Delay_ms(120);
    LCD_2IN8_SendCommand(0x29);
}

/********************************************************************************
function:	Set the resolution and scanning method of the screen
parameter:
		Scan_dir:   Scan direction
********************************************************************************/
static void LCD_2IN8_SetAttributes(UBYTE Scan_dir)
{
    //Get the screen scan direction
    LCD_2IN8.SCAN_DIR = Scan_dir;
    UBYTE MemoryAccessReg = 0x00;

    //Get GRAM and LCD width and height
    if(Scan_dir == HORIZONTAL) {
        LCD_2IN8.HEIGHT	= LCD_2IN8_HEIGHT;
        LCD_2IN8.WIDTH   = LCD_2IN8_WIDTH;
        MemoryAccessReg = 0X78;
    } else {
        LCD_2IN8.HEIGHT	= LCD_2IN8_WIDTH;
        LCD_2IN8.WIDTH   = LCD_2IN8_HEIGHT;
        MemoryAccessReg = 0X00;
    }

    // Set the read / write scan direction of the frame memory
    LCD_2IN8_SendCommand(0x36); //MX, MY, RGB mode
    //LCD_2IN8_SendData_8Bit(MemoryAccessReg);	//0x08 set RGB
	LCD_2IN8_SendData_8Bit(MemoryAccessReg);	//0x08 set RGB
}

/********************************************************************************
function :	Initialize the lcd
parameter:
********************************************************************************/
void LCD_2IN8_Init(UBYTE Scan_dir)
{
    //Turn on the backlight
    LCD_2IN8_BL_1;
    //Hardware reset
    LCD_2IN8_Reset();

    //Set the resolution and scanning method of the screen
    LCD_2IN8_SetAttributes(Scan_dir);
    
    //Set the initialization register
    LCD_2IN8_InitReg();
}

/********************************************************************************
function:	Sets the start position and size of the display area
parameter:
		Xstart 	:   X direction Start coordinates
		Ystart  :   Y direction Start coordinates
		Xend    :   X direction end coordinates
		Yend    :   Y direction end coordinates
********************************************************************************/
void LCD_2IN8_SetWindows(UWORD Xstart, UWORD Ystart, UWORD Xend, UWORD Yend)
{
    //set the X coordinates

    if (LCD_2IN8.SCAN_DIR == VERTICAL) { 
        // set the X coordinates
        LCD_2IN8_SendCommand(0x2A);
        LCD_2IN8_SendData_8Bit(Xstart >> 8);
        LCD_2IN8_SendData_8Bit(Xstart);
        LCD_2IN8_SendData_8Bit((Xend) >> 8);
        LCD_2IN8_SendData_8Bit(Xend);

        // set the Y coordinates
        LCD_2IN8_SendCommand(0x2B);
        LCD_2IN8_SendData_8Bit((Ystart) >> 8);
        LCD_2IN8_SendData_8Bit(Ystart);
        LCD_2IN8_SendData_8Bit((Yend) >> 8);
        LCD_2IN8_SendData_8Bit(Yend);
    }
    else { 
        // set the X coordinates
        LCD_2IN8_SendCommand(0x2A);
        LCD_2IN8_SendData_8Bit((Xstart) >> 8);
        LCD_2IN8_SendData_8Bit(Xstart);
        LCD_2IN8_SendData_8Bit((Xend) >> 8);
        LCD_2IN8_SendData_8Bit(Xend);

        // set the Y coordinates
        LCD_2IN8_SendCommand(0x2B);
        LCD_2IN8_SendData_8Bit(Ystart >> 8);
        LCD_2IN8_SendData_8Bit(Ystart);
        LCD_2IN8_SendData_8Bit((Yend) >> 8);
        LCD_2IN8_SendData_8Bit(Yend);
    }
    LCD_2IN8_SendCommand(0x2C);
}

/******************************************************************************
function :	Clear screen
parameter:
******************************************************************************/
void LCD_2IN8_Clear(UWORD Color)
{
    UWORD j;
    UWORD Image[LCD_2IN8_WIDTH];
    for (j=0; j<LCD_2IN8_WIDTH; j++) {
        Image[j] = Color;
    }
    
    LCD_2IN8_SetWindows(0, 0, LCD_2IN8_WIDTH, LCD_2IN8_HEIGHT);
    LCD_2IN8_DC_1;
    for(j = 0; j < LCD_2IN8_HEIGHT; j++){
        DEV_SPI_Write_nByte((uint8_t *)&Image, LCD_2IN8_WIDTH*2);
    }
}

/******************************************************************************
function :	Sends the image buffer in RAM to displays
parameter:
******************************************************************************/
void LCD_2IN8_Display(UWORD *Image)
{
    UWORD j;
    LCD_2IN8_SetWindows(0, 0, LCD_2IN8_WIDTH, LCD_2IN8_HEIGHT);
    LCD_2IN8_DC_1;
    for (j = 0; j < LCD_2IN8_HEIGHT; j++) {
        DEV_SPI_Write_nByte((uint8_t *)&Image[j*LCD_2IN8_WIDTH], LCD_2IN8_WIDTH*2);
    }

}

void LCD_2IN8_DisplayWindows(UWORD Xstart, UWORD Ystart, UWORD Xend, UWORD Yend, UWORD *Image)
{
    // display
    UDOUBLE Addr = 0;

    UWORD j,data;
	
	if(Xstart > Xend) 
	{
		data = Xstart;
		Xstart = Xend;
		Xend = data;
	}
	if (Ystart > Yend)
	{
		data = Ystart;
		Ystart = Yend;
		Yend = data;
	}
	Xstart = (Xstart < 240)? Xstart : 0;
	Ystart = (Ystart < 320)? Ystart : 0;

    Xend = (Xend < 240)? Xend : 240;
	Yend = (Yend < 320)? Yend : 320;


    LCD_2IN8_SetWindows(Xstart, Ystart, Xend , Yend);
    LCD_2IN8_DC_1;
    for (j = Ystart; j < Yend - 1; j++) {
        Addr = Xstart + j * LCD_2IN8_WIDTH ;
        DEV_SPI_Write_nByte((uint8_t *)&Image[Addr], (Xend-Xstart)*2);
    }
}


void LCD_2IN8_DisplayPoint(UWORD X, UWORD Y, UWORD Color)
{
    LCD_2IN8_SetWindows(X,Y,X,Y);
    LCD_2IN8_SendData_16Bit(Color);
}

void  Handler_2IN8_LCD(int signo)
{
    //System Exit
    printf("\r\nHandler:Program stop\r\n");     
    DEV_ModuleExit();
	exit(0);
}

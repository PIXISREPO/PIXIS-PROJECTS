#include "DEV_Config.h"
#include "LCD_2in8.h"
#include "Touch_2in8.h"
#include "GUI_Paint.h"
#include "GUI_BMP.h"
#include "test.h"
#include "image.h"
#include <stdio.h>		//printf()
#include <stdlib.h>		//exit()
#include <signal.h>     //signal()

UBYTE flag = 0,flgh = 0;
UWORD *BlackImage,x,y,l;

struct Touch_Data{
    uint16_t x; /*!< X coordinate */
    uint16_t y; /*!< Y coordinate */
    uint8_t points;    // Number of touch points
} Touch_Old;
void LCD_2IN8_test(void)
{
    // Exception handling:ctrl + c
    signal(SIGINT, Handler_2IN8_LCD);
    
    /* Module Init */
	if(DEV_ModuleInit() != 0){
        DEV_ModuleExit();
        exit(0);
    }
	
    /* LCD Init */
	printf("2.8inch LCD demo...\r\n");
	LCD_2IN8_Init(VERTICAL);
    Touch_Init();
	LCD_2IN8_Clear(BLACK);
	LCD_SetBacklight(1023);


    UDOUBLE Imagesize = LCD_2IN8_HEIGHT*LCD_2IN8_WIDTH*2;
    printf("Imagesize = %d\r\n", Imagesize);
    if((BlackImage = (UWORD *)malloc(Imagesize)) == NULL) {
        printf("Failed to apply for black memory...\r\n");
        exit(0);
    }
    // /*1.Create a new image cache named IMAGE_RGB and fill it with white*/
    Paint_NewImage(BlackImage, LCD_2IN8_WIDTH, LCD_2IN8_HEIGHT, 0, BLACK, 16);
    Paint_Clear(WHITE);
	Paint_SetRotate(ROTATE_0);
    
    // test 1
    char *BmpPath[3] = {"./pic/LCD_2inch8_1.bmp", "./pic/LCD_2inch8_2.bmp", "./pic/LCD_2inch8_3.bmp"};
    for(UBYTE i=0; i<3; i++) {
        GUI_ReadBmp(BmpPath[i]);
        LCD_2IN8_Display(BlackImage);
        DEV_Delay_ms(1000);
    }
    
    // test 2
    Paint_Clear(BLUE);  
    LCD_2IN8_Display(BlackImage);
    UBYTE Start_Flag = 0,i=0;
    while(1){  
        if(Touch.state){
            Touch.state  = 0;
            if(Touch.points > 1){
                for(i = 0;i < Touch.points;i++){
                    Paint_DrawCircle(Touch.coords[i].x, Touch.coords[i].y,25, YELLOW, DOT_PIXEL_2X2,DRAW_FILL_EMPTY );
                    
                }
                LCD_2IN8_Display(BlackImage);
                Touch_Old.points = Touch.points;
            }
            else{
                if(Touch_Old.points > 1){
                    Paint_Clear(BLUE);
                    Start_Flag = 0;
                    LCD_2IN8_Display(BlackImage);
                }
                if(Start_Flag == 0){
                    Start_Flag = 1;
                    Touch_Old.x = Touch.coords[0].x;
                    Touch_Old.y = Touch.coords[0].y;
                }
                else{
                    Paint_DrawLine  (Touch_Old.x, Touch_Old.y, Touch.coords[0].x, Touch.coords[0].y, MAGENTA ,DOT_PIXEL_2X2,LINE_STYLE_SOLID);
                    Touch_Old.x = Touch.coords[0].x;
                    Touch_Old.y = Touch.coords[0].y;
                    Touch_Old.points = Touch.points;
                    Touch.points = 0;
                }
                LCD_2IN8_Display(BlackImage);
            }
        }
        else if(Touch.state == 0 && Touch.points > 1){
            Touch.points = 0;
            Start_Flag = 0;
            Touch_Old.points = 0;
            Paint_Clear(BLUE);
            LCD_2IN8_Display(BlackImage);
        }
        
    }

    // /* Module Exit */
    // free(BlackImage);
    // BlackImage = NULL;
	// DEV_ModuleExit();
}


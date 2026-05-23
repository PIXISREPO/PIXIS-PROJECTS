/*****************************************************************************
* | File      	:   Touch_1IN69.c
* | Author      :   Waveshare team
* | Function    :   Hardware underlying interface
* | Info        :
*                Used to shield the underlying layers of each master
*                and enhance portability
*----------------
* |	This version:   V1.0
* | Date        :   2022-12-02
* | Info        :   Basic version
*
******************************************************************************/
#include "Touch_2in8.h"

struct CST328_Touch touch_data = {0};
struct CST328_Touch Touch = {0};
/******************************************************************************
function :	read ID 读取ID
parameter:  CST816T : 0xB5
******************************************************************************/
uint16_t CST328_Read_cfg()
{   
    uint8_t buf[24];
    I2C_Write_nByte( HYN_REG_MUT_DEBUG_INFO_MODE, buf, 0);
    I2C_Read_nByte( HYN_REG_MUT_DEBUG_INFO_BOOT_TIME,buf, 4);
    printf("TouchPad_ID:0x%02x,0x%02x,0x%02x,0x%02x\r\n", buf[0], buf[1], buf[2], buf[3]);
    I2C_Read_nByte( HYN_REG_MUT_DEBUG_INFO_RES_X, buf, 4);
    printf("TouchPad_X_MAX:%d    TouchPad_Y_MAX:%d \r\n", buf[1]*256+buf[0],buf[3]*256+buf[2]);

    I2C_Read_nByte( HYN_REG_MUT_DEBUG_INFO_TP_NTX, buf, 24);
    printf("D1F4:0x%02x,0x%02x,0x%02x,0x%02x\r\n", buf[0], buf[1], buf[2], buf[3]);
    printf("D1F8:0x%02x,0x%02x,0x%02x,0x%02x\r\n", buf[4], buf[5], buf[6], buf[7]);
    printf("D1FC:0x%02x,0x%02x,0x%02x,0x%02x\r\n", buf[8], buf[9], buf[10], buf[11]);
    printf("D200:0x%02x,0x%02x,0x%02x,0x%02x\r\n", buf[12], buf[13], buf[14], buf[15]);
    printf("D204:0x%02x,0x%02x,0x%02x,0x%02x\r\n", buf[16], buf[17], buf[18], buf[19]);
    printf("D208:0x%02x,0x%02x,0x%02x,0x%02x\r\n", buf[20], buf[21], buf[22], buf[23]);
    printf("CACA Read:0x%04x\r\n", (((uint16_t)buf[11] << 8) | buf[10]));

    I2C_Write_nByte( HYN_REG_MUT_NORMAL_MODE, buf, 0);
    return (((uint16_t)buf[11] << 8) | buf[10]);
}

/******************************************************************************
function :	reset touch 复位触摸
parameter: 
******************************************************************************/
void CST328_Touch_Reset()
{
    TP_RST_0;
    DEV_Delay_ms(100);
    TP_RST_1;
    DEV_Delay_ms(100);
}



/******************************************************************************
function :	screen initialization 屏幕初始化
parameter:  
******************************************************************************/
uint8_t Touch_Init(void)
{
    // UBYTE Rev;
    CST328_Touch_Reset();
    
    uint16_t Verification = CST328_Read_cfg();
    if(!((Verification==0xCACA)?true:false))
        printf("Touch initialization failed!\r\n");
    
    wiringPiISR(TP_INT,INT_EDGE_FALLING,&Touch_CST328_ISR);
    
    return ((Verification==0xCACA)?true:false);
}


// reads sensor and touches
// updates Touch Points, but if not touched, resets all Touch Point Information
uint8_t Touch_Read_Data(void) {
  uint8_t buf[41];
  uint8_t touch_cnt = 0;
  uint8_t clear = 0;
  // uint8_t Over = 0xAB;
  size_t i = 0,num=0;
  I2C_Read_nByte(ESP_LCD_TOUCH_CST328_READ_Number_REG, buf, 1);
  if ((buf[0] & 0x0F) == 0x00) {                                              // 判断手指数量
    I2C_Write_nByte(ESP_LCD_TOUCH_CST328_READ_Number_REG, &clear, 1);  // No touch data
  } else {
    /* Count of touched points */
    touch_cnt = buf[0] & 0x0F;
    if (touch_cnt > CST328_LCD_TOUCH_MAX_POINTS || touch_cnt == 0) {
      I2C_Write_nByte(ESP_LCD_TOUCH_CST328_READ_Number_REG, &clear, 1);
      return true;
    }
    /* Read all points */
    I2C_Read_nByte(ESP_LCD_TOUCH_CST328_READ_XY_REG, &buf[1], 27);
    /* Clear all */
    I2C_Write_nByte(ESP_LCD_TOUCH_CST328_READ_Number_REG, &clear, 1);
    // Serial.print(" points=%d \r\n",touch_cnt);
    // 在临界区内执行需要保护的代码
    /* Number of touched points */
    if(touch_cnt > CST328_LCD_TOUCH_MAX_POINTS)
        touch_cnt = CST328_LCD_TOUCH_MAX_POINTS;
    touch_data.points = (uint8_t)touch_cnt;
    /* Fill all coordinates */
    for (i = 0; i < touch_cnt; i++) {
      if(i>0) num = 2;
      touch_data.coords[i].x = (uint16_t)(((uint16_t)buf[(i * 5) + 2 + num] << 4) + ((buf[(i * 5) + 4 + num] & 0xF0)>> 4));               
      touch_data.coords[i].y = (uint16_t)(((uint16_t)buf[(i * 5) + 3 + num] << 4) + ( buf[(i * 5) + 4 + num] & 0x0F));
      touch_data.coords[i].strength = ((uint16_t)buf[(i * 5) + 5 + num]);
    }
    // Serial.print(" points=%d \r\n",touch_data.points);
  }
  return true;
}

/*!
    @brief  获取手指坐标位置
	@param	uint16_t *x
			存放各个手指的 X 坐标
	@param	uint16_t *y
			存放各个手指的 Y 坐标
	@param	uint16_t *strength
			存放各个手指的压力
	@param	uint8_t *point_num
			存放手指数量的指针
	@param	uint8_t max_point_num
			最大手指数量
*/
uint8_t Touch_Get_XY(uint16_t *x, uint16_t *y, uint16_t *strength, uint8_t *point_num, uint8_t max_point_num) {
  
  // 在临界区内执行需要保护的代码
  /* Count of points */
  if(touch_data.points > max_point_num)
    touch_data.points = max_point_num;
  for (size_t i = 0; i < touch_data.points; i++) {
      x[i] = touch_data.coords[i].x;
      y[i] = touch_data.coords[i].y;
      if (strength) {
          strength[i] = touch_data.coords[i].strength;
      }
  }
  *point_num = touch_data.points;
  /* Invalidate */
  touch_data.points = 0;
  return (*point_num > 0);
}
void example_touchpad_read(void){
  uint16_t touchpad_x[5] = {0};
  uint16_t touchpad_y[5] = {0};
  uint16_t strength[5]   = {0};
  uint8_t touchpad_cnt = 0;
  Touch_Read_Data();
  uint8_t touchpad_pressed = Touch_Get_XY(touchpad_x, touchpad_y, strength, &touchpad_cnt, CST328_LCD_TOUCH_MAX_POINTS);
  if (touchpad_pressed && touchpad_cnt > 0) {
      Touch.points = touchpad_cnt;
      for (size_t i = 0; i <touchpad_cnt; i++) {
        Touch.coords[i].x = touchpad_x[i];
        Touch.coords[i].y = touchpad_y[i];
      }
      Touch.state = LV_INDEV_STATE_PR;
      printf("Touch : X=%d    Y=%d    num=%d",touchpad_x[0],touchpad_y[0],touchpad_cnt);
  } else {
      Touch.state  = LV_INDEV_STATE_REL;
  }
}
/*!
    @brief  handle interrupts
*/
void Touch_CST328_ISR(void) {
    example_touchpad_read();
}












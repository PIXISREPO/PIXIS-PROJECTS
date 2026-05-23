import time
import smbus
from gpiozero import *
import RPi.GPIO   
CST328_address = 0x1A

TP_INT   = 4
TP_RST   = 17

CST328_LCD_TOUCH_MAX_POINTS = 5
# 定义 CST328_Touch 结构体
class CST328_Touch:
    def __init__(self):
        self.points = 0
        self.coords = [{"x": 0, "y": 0, "strength": 0} for _ in range(CST328_LCD_TOUCH_MAX_POINTS)]
        self.state = 0
class Touch_Data:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.points = 0

cst328_data  =  CST328_Touch()
touch_data  =  CST328_Touch()
Touch_Data_Old  =  Touch_Data()

class Touch_2inch8():
    def __init__(self):
        self.GPIO = RPi.GPIO
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setwarnings(False)
        # #Initialize I2C
        self.I2C = smbus.SMBus(1)
        self.GPIO.setup(TP_INT, self.GPIO.IN,self.GPIO.PUD_UP)
        self.GPIO.setup(TP_RST, self.GPIO.OUT)
        self.GPIO.add_event_detect(TP_INT,self.GPIO.FALLING,self.Int_Callback,5) 
        # pass
        #self.GPIO_TP_INT = Button(TP_INT)                                                  # 使用GPIO Zero库中的Button类
        #self.GPIO_TP_RST = DigitalOutputDevice(TP_RST,active_high = True,initial_value =True)   # 使用GPIO Zero库中的DigitalOutputDevice类
        #self.GPIO_TP_INT.when_pressed = self.Int_Callback  # 中断函数

    def CST328_init(self):
        self.Touch_Reset()
        bRet=self.CST328_Read_cfg()
        if bRet :
            print("Success:Detected CST328.")
        else    :
            print("Error: Not Detected CST328.")
            return None

    def Touch_module_exit(self):
        if self.I2C!=None :
            self.I2C.close()
        self.GPIO_TP_RST.close()
        self.GPIO_TP_INT.close()
        time.sleep(0.001)
        
    def _read_nbyte(self, Reg, num_bytes):
        # 拆分16位寄存器地址成高8位和低8位
        reg_high = (Reg >> 8) & 0xFF
        reg_low = Reg & 0xFF
        # 发送寄存器地址的高8位和低8位
        self.I2C.write_byte_data(CST328_address, reg_high, reg_low)
        # 读取数据
        # 初始化存储读取结果的列表
        data = []
        # 循环读取多个字节数据
        for _ in range(num_bytes):
            rec = self.I2C.read_byte(CST328_address)
            data.append(rec)
        return data
    
    def _write_null(self, Reg):
        # 拆分16位寄存器地址成高8位和低8位
        reg_high = (Reg >> 8) & 0xFF
        reg_low = Reg & 0xFF
        self.I2C.write_byte_data(CST328_address, reg_high, reg_low)

    def _write_nbyte(self, Reg, val):
        # 拆分16位寄存器地址成高8位和低8位
        reg_high = (Reg >> 8) & 0xFF
        reg_low = Reg & 0xFF
        data = [reg_low, val]
        data_int = int.from_bytes(bytes(data), byteorder='big')  # 将列表data转换为整数
        self.I2C.write_byte_data(CST328_address, reg_high, data_int)
    
    def CST328_Read_cfg(self):
        buf = bytearray(24) # 创建包含 24 个uint8_t类型的缓冲区
        HYN_REG_MUT_DEBUG_INFO_MODE         = 0xD101
        HYN_REG_MUT_NORMAL_MODE             = 0xD109
        HYN_REG_MUT_DEBUG_INFO_TP_NTX       = 0xD1F4
        HYN_REG_MUT_DEBUG_INFO_RES_X        = 0xD1F8
        HYN_REG_MUT_DEBUG_INFO_BOOT_TIME    = 0xD1FC

        self._write_null(HYN_REG_MUT_DEBUG_INFO_MODE)
        buf = self._read_nbyte(HYN_REG_MUT_DEBUG_INFO_BOOT_TIME, 4)
        print("TouchPad_ID:" + hex(buf[0]) + "," + hex(buf[1]) + "," + hex(buf[2]) + "," + hex(buf[3]))
        buf = self._read_nbyte(HYN_REG_MUT_DEBUG_INFO_RES_X, 4)
        print("TouchPad_X_MAX:" + str(buf[1]*256+buf[0]) + "    TouchPad_Y_MAX:" + str(buf[3]*256+buf[2]) + "\r\n")

        buf = self._read_nbyte(HYN_REG_MUT_DEBUG_INFO_TP_NTX, 24)
        print("D1F4:" + hex(buf[0]) + "," + hex(buf[1]) + "," + hex(buf[2]) + "," + hex(buf[3]))
        print("D1F8:" + hex(buf[4]) + "," + hex(buf[5]) + "," + hex(buf[6]) + "," + hex(buf[7]))
        print("D1FC:" + hex(buf[8]) + "," + hex(buf[9]) + "," + hex(buf[10]) + "," + hex(buf[11]))
        print("D200:" + hex(buf[12]) + "," + hex(buf[13]) + "," + hex(buf[14]) + "," + hex(buf[15]))
        print("D204:" + hex(buf[16]) + "," + hex(buf[17]) + "," + hex(buf[18]) + "," + hex(buf[19]))
        print("D208:" + hex(buf[20]) + "," + hex(buf[21]) + "," + hex(buf[22]) + "," + hex(buf[23]))
        print("CACA Read:" + hex((buf[11]<< 8) | buf[10]))

        self._write_null(HYN_REG_MUT_NORMAL_MODE)
        if (((buf[11] << 8) | buf[10]) != 0xCACA):
            return False
        return True

    def Int_Callback(self,TP_INT):
        self.Touch_Read_Data()
        self.Touch_Get_XY()
        print("CACA Read:")
        
    #Reset  复位    
    def Touch_Reset(self):
        self.GPIO.output(TP_RST, 0)  
        time.sleep(1 / 1000.0)
        self.GPIO.output(TP_RST, 1)  
        time.sleep(50 / 1000.0)
    
    #Get the coordinates of the touch  获取触摸的坐标
    def Touch_Read_Data(self):
        buf = bytearray(41) # 创建包含41个uint8_t类型的缓冲区
        ESP_LCD_TOUCH_CST328_READ_Number_REG    = 0xD005
        ESP_LCD_TOUCH_CST328_READ_XY_REG        = 0xD000   
        clear = 0
        touch_cnt = 0
        buf = self._read_nbyte( ESP_LCD_TOUCH_CST328_READ_Number_REG, 1)
        if ((buf[0] & 0x0F) == 0x00):                                               # 判断手指数量
           self._write_nbyte(ESP_LCD_TOUCH_CST328_READ_Number_REG,clear)  # No touch data
        else :
            # Count of touched points
            touch_cnt = buf[0] & 0x0F
            if (touch_cnt > CST328_LCD_TOUCH_MAX_POINTS or touch_cnt == 0) :
                self._write_nbyte(ESP_LCD_TOUCH_CST328_READ_Number_REG, clear)
                return True
            
            # Read all points 
            buf = self._read_nbyte( ESP_LCD_TOUCH_CST328_READ_XY_REG, 27)
            # Clear all 
            self._write_nbyte(ESP_LCD_TOUCH_CST328_READ_Number_REG, clear)
            
            # Number of touched points 
            if(touch_cnt > CST328_LCD_TOUCH_MAX_POINTS):
                touch_cnt = CST328_LCD_TOUCH_MAX_POINTS
            cst328_data.points = touch_cnt
            num = 0
            # Fill all coordinates 
            for i in range(touch_cnt):
                if(i>0):
                    num = 2
                cst328_data.coords[i]["x"] = ((buf[(i * 5) + 1 + num] << 4) + ((buf[(i * 5) + 3 + num] & 0xF0)>> 4))               
                cst328_data.coords[i]["y"] = ((buf[(i * 5) + 2 + num] << 4) + ( buf[(i * 5) + 3 + num] & 0x0F))
                cst328_data.coords[i]["strength"] = (buf[(i * 5) + 4 + num])
            #print("Touch : X=" + str(cst328_data.coords[0]["x"]) + "   Y=" + str(cst328_data.coords[0]["y"]) + "   points=" + str(cst328_data.points))

            
    def Touch_Get_XY(self):
        if cst328_data.points :
            for i in range(cst328_data.points):
                touch_data.coords[i]["x"] = cst328_data.coords[i]["x"]
                touch_data.coords[i]["y"] = cst328_data.coords[i]["y"]
                touch_data.coords[i]["strength"]= cst328_data.coords[i]["strength"]
            touch_data.state = 1
        else:
            touch_data.state  = 0   
        touch_data.points = cst328_data.points
        cst328_data.points = 0
        print("Touch : X=" + str(touch_data.coords[0]["x"]) + "   Y=" + str(touch_data.coords[0]["y"]) + "   points=" + str(touch_data.points))
        

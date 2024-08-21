### STM32

单线程，`main.c`调用其它程序

### 树莓派

单线程，`main_control.py`调用其它程序，细节如下



`main_control.py`调用`stm_communication.py`和`imu.py`建立连接。

`main_control.py`调用`camera.py`启动相机。

`main_control.py`调用`algorithm.py`创建算法对象。

循环：

​	`main_control.py`从`stm_communication.py`和`imu.py`读取编码器、超声传感器、IMU输入。

​	`main_control.py`从`camera.py`读取图片，用`vision.py`转化为信息。

​	`main_control.py`用相机信息、编码器、超声传感器、IMU输入更新`algorithm.py`。

​	`main_control.py`调用`stm_communication.py`传递`algorithm.py`得到的电机转速与舵机角度。
# System Design

此为系统设计之总论，诸君必通读之。

## STM32

单线程，`main.c`调用其它程序

`main.c`调用`motor.h`使用控制电机、舵机的函数
`main.c`调用`PID.h`使用PID函数
`main.c`调用`message.h`通过串口向树莓派发送信息

### 传输协定凡例

一、STM32须传乎树莓派之信者，编码器二，超声二。
一、所传之信凡八位，编码器各据二，超声各据二。
一、首二位者编码器一，次二位者编码器二，三二位者超声一，末二位者超声二。

一、树莓派须传乎STM32之信者，校验码一，右轮速（PWM），左轮速（与output列表相反），刷一，盖一，PID参数左右各六。
一、所传之信凡十七位，校验一位，诸轮各据一，刷一，盖一，右轮PID参数据位六，八，十，十二，十四，十六，左轮PID参数据位七，九，十一，十三，十五，十七。参数历为Kp_mul, Kp_frac, Ki_mul, Ki_frac, Kd_mul, Kd_frac。（此为调试之信）

## 树莓派

单线程，`main_control.py`调用其它程序，细节如下

```bash
.
├── main_control.py 调用 stm_communication.py 和 imu.py 建立连接
├── main_control.py 调用 camera.py 启动相机
└── main_control.py 调用 core.py 创建算法对象
```

循环：

```bash
.
├── ​main_control.py 从 stm_communication.py 和 imu.py 读取编码器、超声传感器、IMU输入
├── ​main_control.py 从 camera.py 读取图片，用 vision.py 转化为信息
├── ​main_control.py 用相机信息、编码器、超声传感器、IMU输入更新 core.py
└── ​main_control.py 调用 stm_communication.py 传递 core.py 得到的电机转速与舵机角度
```

### 关于树莓派接收的信息的格式

暂时不用太纠结于格式，只要能把需要的信息传过去就行，我会根据信息格式调整`core.py`。（记得获得信息时的时间也是信息的一部分。）

### 关于运行时间

树莓派跑的不快，又是没有中断的单线程，因此程序的运行时间很重要。我们需要控制每个模块的单次运行时间上限。善用`time.time()`函数。（对模块进行时间测试时，请在树莓派上运行。）

### 关于各个代码文件的细节

`main_control.py`(Mnky负责)

树莓派运行时主进程在这里面循环。

`stm_communication.py`(chaoyiL负责)

启动时与stm32建立串口通讯，开始由外部进程将收到的信息存入缓冲区。被主进程调用`get_encoder_and_ultrasonic_input()`时，返回所有新的信息。被主进程调用`send_output()`时，将需要发送的信息存入输出缓冲区，随后由外部进程发送。（由于收发都是由外部进程进行的，因此这个函数不应当占用主进程的过多市场。期望每次调用函数执行时间不超过2ms。）

`imu.py`(Auto Completed)

与`stm_communication.py`类似，但不存在缓冲区，主进程调用`get_imu_input()`通过串口向IMU发出请求并等待回复。如果IMU在一定时间内（如5ms）没有回复，则请求超时并退出，返回None。更准确地讲，IMU模块始终在输出六轴信息，主进程只是在需要时向IMU发出请求，IMU在收到请求后立即回复（或进行一段时间采样后一并回复）。

`camera.py`(Mnky负责)

启动时打开相机，之后主进程通过`get_image_bgr()`得到相机的即时原始图像。主进程每0.5秒拍一张照。

`vision.py`(Mnky负责)

主进程将原始图像传参给`process()`，返回从图像中识别的信息。这个函数用时较长（约50~150ms），但是

并不是每个主循环都调用，而是每0.5秒调用一次。即便如此，在此期间树莓派也无法向stm32发送电机控制信息。因此，这一文件很可能需要C重写。

`core.py`(Mnky负责)

主进程将得到的信息传递给`update()`，进行规划。这一过程每个循环都进行，不应使用过多时间，应控制在2ms内。随后用`get_output()`得到移动方式信息（这应当在0.1ms内）。

`dummy.py`(Mnky负责)

傀儡系统。由远程连接手动控制的小车活动，与`core.get_output()`类似地输出信号。优先级高于core。

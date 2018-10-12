"""
This module includes the core functions of Geomagic touch haptic device.
Class:  Geo_touch
Methods:    hd_init_device(self, config_name = '')
            hd_get_current_device(self)
            hd_begin_frame(self, geo_touch_handle)
            hd_end_frame(self, geo_touch_handle)

            hd_get_current_position_double(self)
            hd_get_current_velocity_double(self)
            hd_get_current_gimbal_angles_double(self)


            hd_start_scheduler(self)
            hd_stop_scheduler(self)
            hd_schedule_synchronous(self, hd_callback_func)
            hd_schedule_asynchronous(self, hd_callback_func):
"""


from ctypes import *
import threading


HHD = c_uint
HDdouble = c_double
HDint = c_int
HDushort = c_ushort
HDboolean = c_ubyte
HDfloat = c_float
HDCallbackCode = c_uint
HDlong = c_long
HDerror = c_uint
type_HDdouble_array_3 = HDdouble * 3  # ctypes数组
type_HDfloat_array_3 = HDfloat * 3


class Geo_touch(object):
    def __init__(self):

        super(Geo_touch, self).__init__()

        self.rad_to_deg = 57.29578
        self.geo_touch_dll = windll.LoadLibrary('hd.dll')  # 加载 hd.dll动态库
        self.callback_flag = False  # 回调函数执行标志 False: 不执行  True: 可执行
        # 约定ctypes函数参数
        self.geo_touch_dll.hdGetDoublev.argvtypes = [c_uint, POINTER(HDdouble)]
        self.geo_touch_dll.hdGetIntegerv.argvtypes = [c_uint, POINTER(HDint)]
        self.geo_touch_dll.hdGetBooleanv.argvtypes = [c_uint, POINTER(HDboolean)]

    def hd_init_device(self, config_name = ''):
        """
        初始化设备 Geomagic touch
        :param config_name: string 默认值='Default Device' 或 空字符
        :return: HHD 设备句柄
        """
        self.geo_touch_dll.hdInitDevice.argtype = c_char_p
        self.geo_touch_dll.hdInitDevice.restype = HHD
        return self.geo_touch_dll.hdInitDevice(config_name.encode())

    def hd_schedule_synchronous(self, hd_callback_func, priority = 30000):
        """
        部署一个同步任务，传入一个ctypes回调函数
        :param hd_callback_func: 回调函数——用装饰器 @CFUNCTYPE(HDCallbackCode)装饰——第一个参数为返回值，后面参数为传入参数
        :param priority: uint 优先级 默认值30000
        :return: None
        """
        self.geo_touch_dll.hdScheduleSynchronous(hd_callback_func, byref(c_int(0)), HDushort(priority))

    def hd_schedule_asynchronous(self, hd_callback_func, priority = 30000):
        """
        部署一个异步任务，传入一个ctypes回调函数
        :param hd_callback_func: 回调函数——用装饰器 @CFUNCTYPE(HDCallbackCode)装饰——第一个参数为返回值，后面参数为传入参数
        :param priority: uint 优先级 默认值30000
        :return: None
        """
        self.geo_touch_dll.hdScheduleAsynchronous(hd_callback_func, byref(c_int(0)), HDushort(priority))

    def hd_start_scheduler(self):
        """
        开始一个任务, 及线程
        :return: None
        """
        self.callback_flag = True
        self.schedule_thread = threading.Thread(target=self.__schedule_thread_func, name='Schedule_Thread')
        self.schedule_thread.start()

    #线程目标函数
    def __schedule_thread_func(self):
        self.geo_touch_dll.hdStartScheduler()
        while self.callback_flag:
            continue
        self.geo_touch_dll.hdStopScheduler()

    def hd_stop_scheduler(self):
        """
        结束一个任务
        :return: None
        """
        self.callback_flag = False
        self.schedule_thread.join()

    def hd_get_current_device(self):
        """
        获取当前设备句柄
        :return: HHD 设备句柄
        """
        self.geo_touch_dll.hdGetCurrentDevice.restype = HHD
        return self.geo_touch_dll.hdGetCurrentDevice()

    def hd_begin_frame(self, geo_touch_handle):
        """
        开始一帧，帧内数据采集、设置等状态相关操作
        :param geo_touch_handle: 传入要开始一帧的设备句柄
        :return: None
        """
        self.geo_touch_dll.hdBeginFrame.argtype = HHD
        self.geo_touch_dll.hdBeginFrame(geo_touch_handle)

    def hd_end_frame(self, geo_touch_handle):
        """
        结束一帧，该帧状态采集、设置等操作结束
        :param geo_touch_handle: 传入要关闭一帧的设备句柄
        :return: None
        """
        self.geo_touch_dll.hdEndFrame.argtype = HHD
        self.geo_touch_dll.hdEndFrame(geo_touch_handle)

    # 笔记：如何给ctypes函数传入数组变量——引用或指针均可
    def hd_get_current_position_double(self):
        """
        获取当前帧的双精度位置
        :return: 3 double元素的list=[x, y, z]，单位——毫米
        """
        position_array = type_HDdouble_array_3(0, 0, 0)
        self.geo_touch_dll.hdGetDoublev(0x2050, position_array)
        return [position_array[0], position_array[1], position_array[2]]

    # def hd_get_current_velocity_double(self):
    #     """
    #     获取当前帧的双精度速度
    #     :return: 3 double元素的list=[x, y, z]，单位——mm/s
    #     """
    #     velocity_array = type_HDdouble_array_3(0, 0, 0)
    #     self.geo_touch_dll.hdGetDoublev(0x2051, velocity_array)
    #     return [velocity_array[0], velocity_array[1], velocity_array[2]]

    def hd_get_current_joint_angles_double(self, mode='deg'):
        """
        获取当前帧的双精度本体关节角度值
        :param mode: 设定返回值类型弧度或角度（默认deg） mode='deg' or 'rad'
        :return: 3 double元素的list=[x, y, z]，单位——rad or degree
        """
        joint_angles_array = type_HDdouble_array_3(0, 0, 0)
        self.geo_touch_dll.hdGetDoublev(0x2100, joint_angles_array)
        if mode == 'rad':
            return [joint_angles_array[0], joint_angles_array[1], joint_angles_array[2]]
        elif mode == 'deg':
            joint_angles = []
            for i in range(0, 3):
                joint_angles.append(joint_angles_array[i] * self.rad_to_deg)
            return joint_angles
        return None

    def hd_get_current_gimbal_angles_double(self, mode = 'deg'):
        """
        获取当前帧的双精度万向节角度值
        :param mode: 设定返回值类型弧度或角度（默认） mode='deg' or 'rad'
        :return: 3 double元素的list=[x, y, z]，单位——rad or degree
        """
        gimbal_angles_array = type_HDdouble_array_3(0, 0, 0)
        self.geo_touch_dll.hdGetDoublev(0x2150, gimbal_angles_array)
        if mode == 'rad':
            return [gimbal_angles_array[0], gimbal_angles_array[1], gimbal_angles_array[2]]
        elif mode == 'deg':
            gimbal_angles = []
            for i in range(0, 3):
                gimbal_angles.append(gimbal_angles_array[i] * self.rad_to_deg)
            return gimbal_angles
        else:
            return None

    # 笔记：如何给ctypes函数传入一个指针变量
    def hd_get_current_buttons(self):
        """
        获取当前帧按钮状态
        :return: c_long  0-均未被按下   1-深色按钮按下    2-浅色按钮按下    3-均被按下
        """
        n_buttons = c_int(0)  # 先创建一个ctypes对象
        self.geo_touch_dll.hdGetIntegerv(0x2000, byref(n_buttons))  # 然后再将该对象的引用byref 或指针pointer传入ctypes函数
        return n_buttons


# EXAMPLE:
# @CFUNCTYPE(HDCallbackCode)
# def hd_callback_func1():
#     geo_touch.hd_begin_frame(hHd)
#     velocity = geo_touch.hd_get_current_velocity_double()
#     for i in velocity:
#         print(i, end=' ')
#     print('\n')
#     geo_touch.hd_end_frame(hHd)
#     return 1
#
#
# geo_touch = Geo_touch()
# hHd = geo_touch.hd_init_device('Default Device')
# print(hHd)
# geo_touch.hd_schedule_synchronous(hd_callback_func1)
# geo_touch.hd_start_scheduler()





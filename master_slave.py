"""
This module includes the core functions of Geomagic touch haptic device.
Class:
Methods:
"""

from collections import deque
import threading
from ctypes import *

from geomagic_touch_core import GeoTouchLower
from sanxi_core import Sanxi


class GeoCtrlSanXi(Sanxi):
    def __init__(self):
        super(GeoCtrlSanXi, self).__init__()
        self.scaling_factor = 1
        self.touch_position_queue = deque(maxlen=2)
        self.touch_gimbal_angles_queue = deque(maxlen=2)
        # threading Timer
        self.ctrl_timer = None

    def start_ctrl(self):
        geo_touch.touch_handle = geo_touch.hd_init_device('Default Device')
        if geo_touch.touch_handle < 0:
            return False
        else:
            geo_touch.hd_schedule_synchronous(scheduler_call_back_func1)
            geo_touch.hd_start_scheduler()
            # threading Timer
            self.ctrl_timer = threading.Timer(0.05, self.touch_ctrl_sanxi_loop)
            self.ctrl_timer.start()
            return True

    def stop_ctrl(self):
        pass

    def touch_ctrl_sanxi_loop(self):
        # 空闲时清空差值列表
        if geo_touch.touch_button_state == 0:
            self.touch_position_queue.clear()
            self.touch_gimbal_angles_queue.clear()
        elif geo_touch.touch_button_state == 1:
            self.adjust_orientation2()
        elif geo_touch.touch_button_state == 2:
            self.adjust_position()
        self.ctrl_timer = threading.Timer(0.05, self.touch_ctrl_sanxi_loop)
        self.ctrl_timer.start()

    def adjust_position(self):
        self.touch_position_queue.append(geo_touch.touch_current_position)
        if len(self.touch_position_queue) is 2:
            delta_position = [self.touch_position_queue[1][i] - self.touch_position_queue[0][i] for i in range(0, 3)]
            # print(delta_position[0], delta_position[1], delta_position[2])
            self.

    def adjust_orientation2(self):
        pass

    def adjust_orientation3(self):
        pass


@CFUNCTYPE(c_uint)
def scheduler_call_back_func1():
    """

    :return: None
    """
    geo_touch.touch_handle = geo_touch.hd_get_current_device()
    geo_touch.hd_begin_frame(geo_touch.touch_handle)
    geo_touch.touch_current_position = geo_touch.hd_get_current_position()
    geo_touch.touch_current_gimbal_angles = geo_touch.hd_get_current_gimbal_angles()
    geo_touch.touch_button_state = geo_touch.hd_get_current_buttons()
    geo_touch.hd_end_frame(geo_touch.touch_handle)
    return 1


geo_touch = GeoTouchLower()

if __name__ == '__main__':
    geo_ctrl_sanxi = GeoCtrlSanXi()
    geo_ctrl_sanxi.start_ctrl()

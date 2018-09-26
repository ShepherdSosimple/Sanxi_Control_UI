"""
This module includes the core functions of SANXI robot
Class: Sanxi, whose base class is RS232 in communication.py module
Functions: search_origin()

Author: Mr SoSimple
"""

import threading

from communication import Message_control
import time


class Sanxi(Message_control):
    __VE_MAX = 250000  # 最大速度
    __AC_MAX = 250000  # 最大加速度
    __DE_MAX = 250000  # 最大减速度

    def __init__(self):
        super(Sanxi, self).__init__()
        self.__mode = '\x10'

    def search_origin(self):
        """
        启动搜寻原点内置程序，原理：限位光电开关
        :return:
        """
        self.send('\x30')
        time.sleep(0.1)
        self.send('\x10')
        time.sleep(0.1)
        self.send('\x12')
        time.sleep(0.1)

    def back2origin(self, wait=False):
        """
        复位：回到原点
        :return:
        """
        self.send('\x30')
        time.sleep(0.1)
        self.send('\x10')
        time.sleep(0.1)
        self.send('\x15')
        time.sleep(0.1)
        if wait:
            while self.message != '\x10':
                self.send('\x05')
                time.sleep(0.3)

    def stop(self):
        """
        quick stop
        :return:
        """
        self.send('\x30')
        time.sleep(0.2)
        self.send('\x10')
        time.sleep(0.1)

    def set_motion_para(self, vep, acp, dep):
        """
        设置运动参数
        :param vep: 速度百分比
        :param acp: 加速度百分比
        :param dep: 减速度百分比
        :return:
        """
        self.changeto_mode14()
        ve = vep * self.__VE_MAX / 100
        ac = acp * self.__AC_MAX / 100
        de = dep * self.__DE_MAX / 100
        self.send('G07 VE={}\n'.format(str(ve)))
        time.sleep(0.05)
        self.send('G07 AC={}\n'.format(str(ac)))
        time.sleep(0.05)
        self.send('G07 DE={}\n'.format(str(de)))
        time.sleep(0.05)

    def changeto_mode14(self):
        self.send('\x30')
        time.sleep(0.05)
        self.send('\x10')
        time.sleep(0.05)
        self.send('\x14')
        time.sleep(0.0)

    def rect_move(self, mode, **rect_dict):
        """
        直角坐标运动，点对点
        :param mode: mode='p2p' OR mode='line'
        :param rect_dict: 字典——直角坐标目标值，{'X': *, ...}
        :return:
        """
        send_data = ''
        if mode == 'p2p':
            send_data += 'G20 '
        if mode == 'line':
            send_data += 'G21 '
        all_keys = ['X', 'Y', 'Z', 'A', 'B', 'C', 'D']
        for key in all_keys:
            if rect_dict[key] and (rect_dict[key] != ' '):
                send_data += '{0}={1} '.format(key, str(rect_dict[key]))
        send_data += '\n'
        self.changeto_mode14()
        self.send(send_data)

    def multi_joints_motion(self, **j_dict):
        """
        关节运动，点对点
        :param j_dict: 字典——六轴目标值，{'J*': **, ...}
        :return:
        """
        send_data = 'G00 '
        all_keys = []
        for i in range(1, 7):
            all_keys.append('J{}'.format(str(i)))
        for key in all_keys:
            if j_dict[key] and (j_dict[key] != ' '):
                send_data += '{0}={1} '.format(key, str(j_dict[key]))
        send_data += '\n'
        self.changeto_mode14()
        self.send(send_data)

    def single_joint_motion_start(self, n, is_positive):
        """
        第n轴单轴运动
        :param n: 第n轴单动，eg 1   代表第一轴
        :param is_positive: True-顺时针或 向上, False-逆时针或向下
        :return:
        """
        if n in [2, 3, 5]:
            if is_positive:
                send_data = 'J{}+\n'.format(str(n))
            else:
                send_data = 'J{}-\n'.format(str(n))
        else:
            if is_positive:
                send_data = 'J{}-\n'.format(str(n))
            else:
                send_data = 'J{}+\n'.format(str(n))
        self.changeto_mode14()
        self.send(send_data)

    def single_joint_motion_stop(self, n):
        """
        第n轴停止单轴运动
        :param n: 第n轴停止单动，eg 1   代表第一轴
        :return:
        """
        send_data = 'J{}0\n'.format(str(n))
        self.send(send_data)

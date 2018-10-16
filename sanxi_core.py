"""
This module includes the core functions of SANXI robot
Class: Sanxi, whose base class is RS232 in communication.py module
Functions: search_origin()

Author: Mr SoSimple
"""

import threading
import time
import re

from communication import Message_control



class Sanxi(Message_control):
    __VE_MAX = 250000  # 最大速度
    __AC_MAX = 250000  # 最大加速度
    __DE_MAX = 250000  # 最大减速度

    def __init__(self):
        super(Sanxi, self).__init__()
        self.__mode = '\x10'
        self.return_code = ''  # Sanxi串口返回数据
        self.jn_value = []  # 伪实时关节空间坐标值
        self.xyz_value = []  # 伪实时笛卡尔空间坐标值
        self.start_update_sanxi_output_timer = None
        # 正则表达式预编译
        self.G_detect_pattern = re.compile(r'.*G.*')  # 检测 G字符 与下面表达式联合抽取返回的坐标值
        self.jn_pattern = re.compile(r'.*J1=(.*) J2=(.*) J3=(.*) J4=(.*) J5=(.*) J6=(.*)[\r\s]')
        self.xyz_pattern = re.compile(r'.*X=(.*) Y=(.*) Z=(.*) A=(.*) B=(.*) C=(.*) D=(.*)[\r\s]')



    def connect_sanxi(self, port_name):
        """
        连接三喜机器人
        :param port_name: string，串口名称 example：port_name='COM3'
        :return: Bool
        """
        self.set_port(port_name)
        self.set_baud_rate(115200)
        self.set_timeout(0.1)
        if self.connect() is True:
            return True
        else:
            return False

    def disconnect_sanxi(self):
        """
        断开三喜机器人串口连接
        :return: Bool
        """
        if self.disconnect():
            return True
        else:
            return False


    def start_update_sanxi_output(self):
        """
        开始更新机器人返回的消息，包括坐标信息
        :return: None
        """
        self.start_refresh()
        self.start_update_sanxi_output_timer = threading.Timer(0.01, self.__extract_output_info)
        self.start_update_sanxi_output_timer.start()

    def __extract_output_info(self):
        """
        接收返回消息并抽取返回消息中的坐标信息
        :return: None
        """
        # print('enter extract_output_info')
        if self.return_code != self.message:
            # update return_code
            self.return_code = self.message
            # print('return code =', self.return_code)
            # update state info
            jn_match = self.jn_pattern.match(str(self.return_code))  # 正则表达式匹配
            xyz_match = self.xyz_pattern.match(str(self.return_code))
            G_match = self.G_detect_pattern.match(str(self.return_code))
            # print(jn_match, xyz_match, G_match)
            if G_match is None:
                if jn_match:
                    self.jn_value.clear()
                    for i in range(1, 7):
                        self.jn_value.append(jn_match.group(i))
                if xyz_match:
                    self.xyz_value.clear()
                    for i in range(1, 8):
                        self.xyz_value.append(xyz_match.group(i))
        self.start_update_sanxi_output_timer = threading.Timer(0.01, self.__extract_output_info)
        self.start_update_sanxi_output_timer.start()
        # print('leave extract_output_info')

    def stop_update_sanxi_output(self):
        """
        停止更新机器人返回的消息，包括坐标信息
        :return: None
        """
        self.start_update_sanxi_output_timer.cancel()
        self.stop_refresh()

    def search_origin(self):
        """
        启动搜寻原点内置程序，原理：限位光电开关
        :return: None
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
        :return: None
        """
        self.send('\x30')
        time.sleep(0.1)
        self.send('\x10')
        time.sleep(0.1)
        self.send('\x15')
        time.sleep(0.1)
        if wait:
            while self.return_code != '\x10':
                self.send('\x05')
                time.sleep(0.3)

    def stop(self):
        """
        quick stop
        :return: None
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
        :return: None
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

    def set_return_data_mode(self, mode='cartesian space'):
        """
        设置返回数据模式，直角坐标模式 或 关节坐标模式，默认前者
        :param mode: string
        :return: Bool
        """
        if mode == 'cartesian space':
            self.send('G07 GCM=1\n')
            return True
        elif mode == 'joint space':
            self.send('G07 GCM=0\n')
            return True
        else:
            return False

    def changeto_mode14(self):
        self.send('\x30')
        time.sleep(0.05)
        self.send('\x10')
        time.sleep(0.05)
        self.send('\x14')
        time.sleep(0.02)

    def rect_move(self, mode, **rect_dict):
        """
        直角坐标运动，点对点, 或直线
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
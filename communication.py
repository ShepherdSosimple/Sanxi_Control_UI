"""
This communication module includes RS232 communicating with SANXI robot
Class: RS232 provides fundamental serial operations, including connect, disconnect, send and receive messages
       Message_control provides high level serial and message operations, including a thread  to monitor the message
         received from the serial, and other message handling methods such as changing to hex or ASCII.
Functions: RS232  connect() disconnect() send() receive()
           Message_control  start_refresh() stop_refresh()
Author: Mr SoSimple
"""

import serial
import time
import threading


class RS232(object):
    def __init__(self):
        super(RS232, self).__init__()
        self.__baudrate = 115200
        self.__timeout = 0.2
        # 串口状态机
        self.__connect_state = False  # 串口打开状态
        self.__ser = serial.Serial()

    def set_port(self, portname):
        self.__portname = portname

    def connect(self):
        try:
            # 设置端口、波特率、接收超时
            self.__ser.port = self.__portname
            self.__ser.baudrate = self.__baudrate
            self.__ser.timeout = self.__timeout
            self.__ser.open()
        except Exception as e:
            print('Connect data error: ', e)
        else:
            if self.__ser.isOpen():
                self.__connect_state = True
                return True
            else:
                self.__connect_state = False
                return False

    def is_connected(self):
        if self.__connect_state:
            return True
        else:
            return False

    def disconnect(self):
        try:
            self.__ser.close()
        except Exception as e:
            print('Close port error:', e)
        else:
            if self.__ser.isOpen():
                self.__connect_state = True
                return False
            else:
                self.__connect_state = False
                return True

    def send(self, send_data):
        try:
            self.__ser.write(send_data.encode())
        except Exception as e:
            print('Send data error: ', e)

    def receive(self):
        try:
            receive_data = self.__ser.readline().decode()
            return receive_data
        except Exception as e:
            print('Receive data error: ', e)


class Message_control(RS232):
    def __init__(self):
        super().__init__()
        self.__stopped = False
        self.message = ''

    def __thread_func_refresh(self):
        while not self.__stopped:
            temp = self.receive()
            if temp:
                self.message = temp

    def start_refresh(self):
        self.__stopped = False
        self.t = threading.Thread(target=self.__thread_func_refresh,
                                  name='thread_func_refresh')
        self.t.start()

    def stop_refresh(self):
        self.__stopped = True

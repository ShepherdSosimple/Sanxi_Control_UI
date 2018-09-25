"""
This module includes the functions of sanxiUI.
Related modules: sanxi_core.py, Sanxi_CtrlUI.py
Author:Mr Sosimple
"""
from sanxi_core import Sanxi
from Sanxi_CtrlUI import Ui_Sanxi_form
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
import threading
from PyQt5.QtCore import QCoreApplication
import time
from PyQt5.QtCore import QTimer
import re


class Sanxi_window(Sanxi, QtWidgets.QWidget, Ui_Sanxi_form):
    def __init__(self):
        super(Sanxi_window, self).__init__()
        self.setupUi(self)

        self.return_code = ''
        self.jn_value = []
        self.xyz_value = []
        # 正则表达式预编译
        self.jn_pattern = re.compile(r'.*J1=(.*) J2=(.*) J3=(.*) J4=(.*) J5=(.*) J6=(.*)[\r\s]')
        self.xyz_pattern = re.compile(r'.*X=(.*) Y=(.*) Z=(.*) A=(.*) B=(.*) C=(.*) D=(.*)[\r\s]')
        # communication/start up
        self.connect_pushButton.clicked.connect(self.connect_pushButton_clicked)
        self.searchorigin_pushButton.clicked.connect(self.searchorigin_pushButton_clicked)
        self.disconnct_pushButton.clicked.connect(self.disconnct_pushButton_clicked)
        # motion parameters
        self.motionparaOK_pushButton.clicked.connect(self.motionparaOK_pushButton_clicked)
        # core functions
        self.backtoorigin_pushButton.clicked.connect(self.backtoorigin_pushButton_clicked)
        self.stop_pushButton.clicked.connect(self.stop_pushButton_clicked)
        self.call_v51exe_pushButton.clicked.connect(self.call_v51exe_pushButton_clicked)
        self.resetq_pushButton.clicked.connect(self.resetq_pushButton_clicked)
        # fundamental functions
        self.p2p_pushButton.clicked.connect(self.p2p_pushButton_clicked)
        self.goline_pushButton.clicked.connect(self.goline_pushButton_clicked)
        self.goangle_pushButton.clicked.connect(self.goangle_pushButton_clicked)
        self.sendcode_pushButton.clicked.connect(self.sendcode_pushButton_clicked)
        # display board-timer
        self.display_board_timer = QTimer(self)
        self.display_board_timer.start(100)
        self.display_board_timer.timeout.connect(self.display_board)
        # display board-control button
        self.rectmode_pushButton.clicked.connect(self.rectmode_pushButton_clicked)
        self.anglemode_pushButton.clicked.connect(self.anglemode_pushButton_clicked)
        # single joint jogging
        self.j1cw_pushButton.pressed.connect(self.j1cw_pushButton_pressed)
        self.j1cw_pushButton.clicked.connect(self.j1cw_pushButton_clicked)
        self.j1ccw_pushButton.pressed.connect(self.j1ccw_pushButton_pressed)
        self.j1ccw_pushButton.clicked.connect(self.j1ccw_pushButton_clicked)
        self.j2up_pushButton.pressed.connect(self.j2up_pushButton_pressed)
        self.j2up_pushButton.clicked.connect(self.j2up_pushButton_clicked)
        self.j2down_pushButton.pressed.connect(self.j2down_pushButton_pressed)
        self.j2down_pushButton.clicked.connect(self.j2down_pushButton_clicked)
        self.j3up_pushButton.pressed.connect(self.j3up_pushButton_pressed)
        self.j3up_pushButton.clicked.connect(self.j3up_pushButton_clicked)
        self.j3down_pushButton.pressed.connect(self.j3down_pushButton_pressed)
        self.j3down_pushButton.clicked.connect(self.j3down_pushButton_clicked)
        self.j4cw_pushButton.pressed.connect(self.j4cw_pushButton_pressed)
        self.j4cw_pushButton.clicked.connect(self.j4cw_pushButton_clicked)
        self.j4ccw_pushButton.pressed.connect(self.j4ccw_pushButton_pressed)
        self.j4ccw_pushButton.clicked.connect(self.j4ccw_pushButton_clicked)
        self.j5up_pushButton.pressed.connect(self.j5up_pushButton_pressed)
        self.j5up_pushButton.clicked.connect(self.j5up_pushButton_clicked)
        self.j5down_pushButton.pressed.connect(self.j5down_pushButton_pressed)
        self.j5down_pushButton.clicked.connect(self.j5down_pushButton_clicked)
        self.j6cw_pushButton.pressed.connect(self.j6cw_pushButton_pressed)
        self.j6cw_pushButton.clicked.connect(self.j6cw_pushButton_clicked)
        self.j6ccw_pushButton.pressed.connect(self.j6ccw_pushButton_pressed)
        self.j6ccw_pushButton.clicked.connect(self.j6ccw_pushButton_clicked)

    ##############################connection judgement then raise dialogs########################
    def not_connect_dialog(self):
        QMessageBox.Warning(self, 'Error', 'Please connect first!', QMessageBox.Yes)

    ##############################communication/start up##############################
    def connect_pushButton_clicked(self):
        port_number = self.port_spinBox.value()
        portname = 'COM' + str(port_number)
        self.set_port(portname)
        if self.connect():
            QMessageBox.information(self, 'Info', 'Connected!', QMessageBox.Yes)
            self.start_refresh()
            self.motionparaOK_pushButton_clicked()
        else:
            QMessageBox.information(self, 'Warning', 'Connect Failed', QMessageBox.Yes)

    def searchorigin_pushButton_clicked(self):
        if not self.is_connected():
            self.not_connect_dialog()
        self.search_origin()

    def disconnct_pushButton_clicked(self):
        self.stop_refresh()
        self.disconnect()

    ##############################motion parameters###########################
    def motionparaOK_pushButton_clicked(self):
        vep = self.ve_verticalSlider.value()
        acp = self.ac_verticalSlider.value()
        dep = self.de_verticalSlider.value()
        self.set_motion_para(vep, acp, dep)

    ##############################Core Functions##############################
    def backtoorigin_pushButton_clicked(self):
        if not self.is_connected():
            self.not_connect_dialog()
        self.back2origin()

    def stop_pushButton_clicked(self):
        if not self.is_connected():
            self.not_connect_dialog()
        self.stop()

    # 调用外部exe——三喜原厂软件
    def call_v51exe_pushButton_clicked(self):
        import os
        if (self.is_connected()):
            reply = QMessageBox.information(self, 'Warning',
                                            'Do you want to disconnect first?(Recommend Yes)',
                                            QMessageBox.Yes | QMessageBox.No)
            if reply:
                self.disconnect()
        os.popen('V51.exe')

    # 复位并退出：多线程模式下进行???????????????????????????????????
    def resetq_pushButton_clicked(self):
        if not self.is_connected():
            self.not_connect_dialog()
        else:
            resetquit_thread = threading.Thread(target=self.thread_func_resetquit,
                                                name='Thread-resetquit')
            resetquit_thread.start()
            resetquit_thread.join()
            print('resetquit_thread has dead')
            QCoreApplication.quit()

    def thread_func_resetquit(self):
        print(threading.current_thread().name)
        self.back2origin(wait=True)
        self.stop()
        self.disconnect()

    ##############################Fundamental Functions##############################
    #读直角坐标文本框值
    def read_rect_lineEdit(self):
        rect_dict = {'X': self.xread_lineEdit.text(),
                     'Y': self.yread_lineEdit.text(),
                     'Z': self.zread_lineEdit.text(),
                     'A': self.aread_lineEdit.text(),
                     'B': self.bread_lineEdit.text(),
                     'C': self.cread_lineEdit.text()}
        return rect_dict

    #读关节坐标文本框值
    def read_angle_lineEdit(self):
        j_dict = {'J1': self.j1read_lineEdit.text(),
                  'J2': self.j2read_lineEdit.text(),
                  'J3': self.j3read_lineEdit.text(),
                  'J4': self.j4read_lineEdit.text(),
                  'J5': self.j5read_lineEdit.text(),
                  'J6': self.j6read_lineEdit.text()}
        return j_dict

    #直角坐标点对点运动
    def p2p_pushButton_clicked(self):
        rect_dict = self.read_rect_lineEdit()
        rect_dict['D'] = '0'
        self.rect_move(mode='p2p', **rect_dict)

    #直角坐标直线运动
    def goline_pushButton_clicked(self):
        rect_dict = self.read_rect_lineEdit()
        rect_dict['D'] = '0'
        self.rect_move(mode='line', **rect_dict)

    #按轴角度运动
    def goangle_pushButton_clicked(self):
        j_dict = self.read_angle_lineEdit()
        self.multi_joints_motion(**j_dict)

    #发送命令
    def sendcode_pushButton_clicked(self):
        data_list = self.sendcode_textEdit.toPlainText().split(sep='\n') #拆分多行命令，间隔0.1秒发送
        self.changeto_mode14()
        for send_data in data_list:
            if send_data:
                self.send(send_data + '\n')

    #########################sigle jiont jogging#########################
    # 单轴点动：pressed为按下按钮操作，clicked为松开按钮操作
    def j1cw_pushButton_pressed(self):
        self.single_joint_motion_start(1, True)

    def j1cw_pushButton_clicked(self):
        self.single_joint_motion_stop(1)

    def j1ccw_pushButton_pressed(self):
        self.single_joint_motion_start(1, False)

    def j1ccw_pushButton_clicked(self):
        self.single_joint_motion_stop(1)

    def j2up_pushButton_pressed(self):
        self.single_joint_motion_start(2, True)

    def j2up_pushButton_clicked(self):
        self.single_joint_motion_stop(2)

    def j2down_pushButton_pressed(self):
        self.single_joint_motion_start(2, False)

    def j2down_pushButton_clicked(self):
        self.single_joint_motion_stop(2)

    def j3up_pushButton_pressed(self):
        self.single_joint_motion_start(3, True)

    def j3up_pushButton_clicked(self):
        self.single_joint_motion_stop(3)

    def j3down_pushButton_pressed(self):
        self.single_joint_motion_start(3, False)

    def j3down_pushButton_clicked(self):
        self.single_joint_motion_stop(3)

    def j4cw_pushButton_pressed(self):
        self.single_joint_motion_start(4, True)

    def j4cw_pushButton_clicked(self):
        self.single_joint_motion_stop(4)

    def j4ccw_pushButton_pressed(self):
        self.single_joint_motion_start(4, False)

    def j4ccw_pushButton_clicked(self):
        self.single_joint_motion_stop(4)

    def j5up_pushButton_pressed(self):
        self.single_joint_motion_start(5, True)

    def j5up_pushButton_clicked(self):
        self.single_joint_motion_stop(5)

    def j5down_pushButton_pressed(self):
        self.single_joint_motion_start(5, False)

    def j5down_pushButton_clicked(self):
        self.single_joint_motion_stop(5)

    def j6cw_pushButton_pressed(self):
        self.single_joint_motion_start(6, True)

    def j6cw_pushButton_clicked(self):
        self.single_joint_motion_stop(6)

    def j6ccw_pushButton_pressed(self):
        self.single_joint_motion_start(6, False)

    def j6ccw_pushButton_clicked(self):
        self.single_joint_motion_stop(6)

    #########################display board#########################
    def display_board(self):
        """
        显示接收代码，显示关节坐标值或直角坐标值
        :return:
        """
        if self.return_code != self.message:
            # refresh return_code text_browser
            self.return_code = self.message
            self.returncode_textBrowser.append(self.return_code)
            # refresh value
            jn_match = self.jn_pattern.match(str(self.return_code)) # 正则表达式匹配
            xyz_match = self.xyz_pattern.match(str(self.return_code))
            if jn_match:
                self.jn_value.clear()
                for i in range(1,7):
                    self.jn_value.append(jn_match.group(i))
                # 显示关节坐标
                self.j1show_lineEdit.setText(self.jn_value[0])
                self.j2show_lineEdit.setText(self.jn_value[1])
                self.j3show_lineEdit.setText(self.jn_value[2])
                self.j4show_lineEdit.setText(self.jn_value[3])
                self.j5show_lineEdit.setText(self.jn_value[4])
                self.j6show_lineEdit.setText(self.jn_value[5])
            if xyz_match:
                self.xyz_value.clear()
                for i in range(1,8):
                    self.xyz_value.append(xyz_match.group(i))
                self.xshow_lineEdit.setText(self.xyz_value[0])
                self.yshow_lineEdit.setText(self.xyz_value[1])
                self.zshow_lineEdit.setText(self.xyz_value[2])
                self.ashow_lineEdit.setText(self.xyz_value[3])
                self.bshow_lineEdit.setText(self.xyz_value[4])
                self.cshow_lineEdit.setText(self.xyz_value[5])

    def rectmode_pushButton_clicked(self):
        """
        直角坐标显示模式
        :return:
        """
        self.j1show_lineEdit.clear()
        self.j2show_lineEdit.clear()
        self.j3show_lineEdit.clear()
        self.j4show_lineEdit.clear()
        self.j5show_lineEdit.clear()
        self.j6show_lineEdit.clear()
        self.send('G07 GCM=1\n')

    def anglemode_pushButton_clicked(self):
        """
        关节坐标显示模式
        :return:
        """
        self.xshow_lineEdit.clear()
        self.yshow_lineEdit.clear()
        self.zshow_lineEdit.clear()
        self.ashow_lineEdit.clear()
        self.bshow_lineEdit.clear()
        self.cshow_lineEdit.clear()
        self.send('G07 GCM=0\n')
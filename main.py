
import sys
from SanxiUI_function import Sanxi_window
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myshow = Sanxi_window()
    myshow.show()
    sys.exit(app.exec_())
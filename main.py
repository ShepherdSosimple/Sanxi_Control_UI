
import sys
from SanxiUI_function import Sanxi_window
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_show = Sanxi_window()
    my_show.show()
    sys.exit(app.exec_())
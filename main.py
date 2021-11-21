import sys
import os


from PyQt5.QtWidgets import QApplication
from board import Board
import math


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('PyQt Checkers')
    # app.setWindowIcon(QtGui.QIcon(QPixmap('./assets/icon.png')))
    widget = Board()
    widget.show()
    sys.exit(app.exec_())

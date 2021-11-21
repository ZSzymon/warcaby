import os
from settings import ASSETS_ROOT, SQUARE_SIZE, FIELD_SIZE
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap
from enum import Enum
from PyQt5.QtCore import Qt, QPoint
from PyQt5 import QtGui, QtCore
from colors import Color

class Pawn(QLabel):
    row: int = None
    col: int = None
    color: Color = None
    current_move_pawn = None

    @staticmethod
    def isDifferentColor(p1, p2):
        return p1.color != p2.color

    def __init__(self, row, col, color: Color, window):
        super(Pawn, self).__init__(window)
        self.row = row
        self.col = col
        self.color = color
        self.setScaledContents(True)
        color_path = os.path.join(ASSETS_ROOT, f"{color.name}_pawn.png")
        pixmap = QPixmap(color_path)
        pixmap = pixmap.scaled(SQUARE_SIZE, SQUARE_SIZE)
        self.setPixmap(pixmap)
        self.resize(SQUARE_SIZE, SQUARE_SIZE)
        self.posx = col * SQUARE_SIZE
        self.posy = row * SQUARE_SIZE
        self.move(self.posx, self.posy)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            Pawn.current_move_pawn = self
            print(f"Pressed at pawn: Row:{self.row} Col:{self.col}")
            # print(f"Clicked at pos: {event.pos()}")

    def move(self, x=None, y=None, point=None, square=None):
        if point:
            x = int(point.x())
            y = int(point.y())
        if square:
            self.row = square.pos[0]
            self.col = square.pos[1]
        super().move(x, y)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if event.buttons() & QtCore.Qt.LeftButton:
            drag = QtGui.QDrag(self)
            mimedata = QtCore.QMimeData()
            mimedata.setData('Pawn', bytearray('Pawn', 'utf8'))
            mimedata.setProperty('offset', QPoint(event.x(), event.y()))
            mimedata.setProperty('index', QPoint(self.row, self.col))
            drag.setMimeData(mimedata)
            print(mimedata)
            drag.setDragCursor(QPixmap(os.path.join(ASSETS_ROOT, 'emptyCursor.png')), QtCore.Qt.MoveAction)
            drag.setPixmap(self.pixmap())
            drag.setHotSpot(event.pos())
            self.hide()
            drag.exec_(Qt.CopyAction | Qt.MoveAction)

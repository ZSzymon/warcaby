import sys
import os
from settings import ASSETS_ROOT, SQUARE_SIZE, FIELD_SIZE
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap
from enum import Enum
from PyQt5.QtCore import Qt, QPoint
from PyQt5 import QtGui, QtCore
import math


class Color(Enum):
    black = 0
    white = 1


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
            point = QPoint(self.row, self.col)
            mimedata.setProperty('offset', QPoint(event.x(), event.y()))
            mimedata.setProperty('index', QPoint(self.row, self.col))
            # print(f"Offset: {QPoint(event.row(), event.col())}")
            drag.setMimeData(mimedata)
            print(mimedata)
            drag.setDragCursor(QPixmap(os.path.join(ASSETS_ROOT, 'emptyCursor.png')), QtCore.Qt.MoveAction)
            drag.setPixmap(self.pixmap())
            drag.setHotSpot(event.pos())
            self.hide()
            drag.exec_(Qt.CopyAction | Qt.MoveAction)


class Square:
    pawn: Pawn = None
    pos = None
    color: Color = None

    def getPos(self):
        return self.absolute_pos

    def __init__(self, row, col):
        self.pos = (row, col)
        self.size = (SQUARE_SIZE, SQUARE_SIZE)
        self.absolute_pos = QPoint(col * SQUARE_SIZE, row * SQUARE_SIZE)
        self.color = Square.get_color(row, col)

    @staticmethod
    def get_color(x, y):
        if x % 2 == 0 and y % 2 == 1:
            return Color.black
        if x % 2 == 1 and y % 2 == 0:
            return Color.black

        return Color.white

    @staticmethod
    def jump_distance(old_square, new_square):
        old_row, old_col = old_square.pos
        new_row, new_col = new_square.pos
        if abs(old_row - new_row) == 1 and abs(old_col - new_col) == 1:
            return 1
        if abs(old_row - new_row) == 2 and abs(old_col - new_col) == 2:
            return 2
        return -1

    @staticmethod
    def is_proper_jump(old_square, new_square):
        old_row, old_col = old_square.pos
        new_row, new_col = new_square.pos
        if Pawn.isDifferentColor(old_square, new_square):
            return False
        if abs(old_row - new_row) == 1 and abs(old_col - new_col) == 1:
            return True
        if abs(old_row - new_row) == 2 and abs(old_col - new_col) == 2:
            return True
        return False

    @staticmethod
    def get_jump_direction(old_square, new_square):
        old_row, old_col = old_square.pos
        new_row, new_col = new_square.pos
        return "UP" if new_row - old_row < 0 else "DOWN", "LEFT" if new_col - old_col < 0 else "RIGHT"

    def is_black(self):
        return Square.get_color(self.pos[0], self.pos[1]) == Color.black

    def is_occupied(self):
        return self.pawn is not None

    def set_pawn(self, pawn):
        self.pawn = pawn


class Board(QWidget):
    pawns: list = None
    squares: list
    background: QLabel = None
    white_pawns: list = []
    black_pawns: list = []

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self._init_game_background()
        self._init_squares()
        self._init_black_pawns()
        self._init_white_pawns()

    def _init_game_background(self):
        self.background = QLabel(self)
        self.background.setScaledContents(True)
        self.background.setPixmap(QPixmap(os.path.join(ASSETS_ROOT, "background.png")))
        self.background.setGeometry(0, 0, FIELD_SIZE, FIELD_SIZE)

    def _init_squares(self):
        self.squares = []
        for row in range(8):
            tmp_squares = []
            for col in range(8):
                square = Square(row, col)
                tmp_squares.append(square)
            self.squares.append(tmp_squares)

    def _init_white_pawns(self):
        self.white_checkers = []
        for row in range(0, 3):
            for col in range(8):
                if self.squares[row][col].is_black():
                    pawn = Pawn(row, col, Color.white, self)
                    self.squares[row][col].set_pawn(pawn)

    def _init_black_pawns(self):
        self.black_checkers = []
        for row in range(5, 8):
            for col in range(8):
                if self.squares[row][col].is_black():
                    pawn = Pawn(row, col, Color.black, self)
                    self.squares[row][col].set_pawn(pawn)

    def get_square(self, point: QPoint):
        row = int(point.y() // SQUARE_SIZE)
        col = int(point.x() // SQUARE_SIZE)
        square = self.squares[row][col]
        if square is None:
            stop = 1
        return square

    def get_middle_square(self, old_square: Square, new_square: Square):
        old_row, old_col = old_square.pos
        new_row, new_col = new_square.pos
        direction_vertical = "UP" if new_row - old_row < 0 else "DOWN"
        direction_horizontal = "LEFT" if new_col - old_col < 0 else "RIGHT"
        middle_row = old_row - 1 if direction_vertical == "UP" else old_row + 1
        middle_col = old_col + 1 if direction_horizontal == "RIGHT" else old_col - 1
        return self.squares[middle_row][middle_col]

    def can_transport(self, old_square: Square, new_square: Square):
        jump_distance = Square.jump_distance(old_square, new_square)
        if jump_distance == -1:
            return False
        if not Square.is_proper_jump(old_square, new_square):
            return False
        if jump_distance == 1 and not new_square.is_occupied():
            return True
        if jump_distance == 2 and not new_square.is_occupied():
            middle_square = self.get_middle_square(old_square, new_square)
            differentColor = Pawn.isDifferentColor(middle_square.pawn, old_square.pawn)
            if middle_square.is_occupied() and Pawn.isDifferentColor(middle_square.pawn, old_square.pawn):
                return True
        return False

    def handle_terminate_middle_pawn(self, middle_square):
        color = middle_square.pawn.color
        middle_square.pawn.hide()
        middle_square.pawn = None

    def handle_transport_pawn(self, old_square: Square, new_square: Square):
        pawn = old_square.pawn
        old_square.pawn = None
        new_square.pawn = pawn
        if Square.jump_distance(old_square, new_square) == 2:
            middle = self.get_middle_square(old_square, new_square)
            self.handle_terminate_middle_pawn(middle)
        pawn.move(point=new_square.getPos(), square=new_square)
        pawn.show()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('Pawn'):
            mime = event.mimeData()
            old_square = self.squares[mime.property('index').x()][mime.property('index').y()]
            pawn = old_square.pawn
            new_square = self.get_square(event.pos())
            if new_square and old_square != new_square:
                if self.can_transport(old_square, new_square):
                    self.handle_transport_pawn(old_square, new_square)
                pawn.show()
                event.setDropAction(QtCore.Qt.MoveAction)
                event.accept()
            else:
                pawn.show()
                event.ignore()
        else:
            event.ignore()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('Pawn'):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('PyQt Checkers')
    # app.setWindowIcon(QtGui.QIcon(QPixmap('./assets/icon.png')))
    widget = Board()
    widget.show()
    sys.exit(app.exec_())

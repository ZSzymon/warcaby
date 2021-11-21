import os
from settings import ASSETS_ROOT, SQUARE_SIZE, FIELD_SIZE
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap
from enum import Enum
from PyQt5.QtCore import Qt, QPoint
from PyQt5 import QtGui, QtCore

from square import Square
from pawn import Pawn
from colors import Color
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

    def get_middle_square(self, old_square, new_square):
        old_row, old_col = old_square.pos
        new_row, new_col = new_square.pos
        direction_vertical = "UP" if new_row - old_row < 0 else "DOWN"
        direction_horizontal = "LEFT" if new_col - old_col < 0 else "RIGHT"
        middle_row = old_row - 1 if direction_vertical == "UP" else old_row + 1
        middle_col = old_col + 1 if direction_horizontal == "RIGHT" else old_col - 1
        return self.squares[middle_row][middle_col]

    def can_transport(self, old_square, new_square):
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

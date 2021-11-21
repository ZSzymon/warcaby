
from pawn import Pawn
from settings import ASSETS_ROOT, SQUARE_SIZE, FIELD_SIZE
from colors import Color
from settings import SQUARE_SIZE

from PyQt5.QtCore import Qt, QPoint

class Square:
    pawn = None
    pos = None
    color = None

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
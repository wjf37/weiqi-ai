import numpy as np

class Board:
    def __init__(self, size=19):
        self.size = size
        self.board = np.zeros((size, size), np.uint8)

    def check_in_bounds(self, x, y):
        if x in range(self.size) and y in range(self.size):
            return True
        return False
    
    def place_stone(self, x, y, colour):
        #if x not in range(self.size) and y not in range(self.size):
        #    return False
        if self.board[x,y] == 0:
            self.board[x,y] = colour
            return True
        return False
    
    def remove_stone(self, x, y):
        #if x not in range(self.size) and y not in range(self.size):
        #    return False
        if self.board[x,y] != 0:
            self.board[x,y] = 0
            return True
        return False
    
    def liberties_check(self, colour):
        return True
    #make groups of connected stones
    #check liberties of stones
    #
    #check if in atari
    #check if suicide move
    #check for repeated board state
    #
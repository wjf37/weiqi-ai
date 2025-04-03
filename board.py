import numpy as np
from collections import deque

class Board:
    def __init__(self, size=19):
        #colour 0 = empty colour 1 = black colour 2 = white
        self.size = size
        self.board = np.zeros((size, size), np.uint8)

        self.directions = {
            1: [0,1],
            2:[0,-1],
            3:[1,0],
            4:[-1,0]
        }

    def check_in_bounds(self, x, y):
        if x in range(self.size) and y in range(self.size):
            return True
        return False
    
    def place_stone(self, x, y, colour):
        #if x not in range(self.size) and y not in range(self.size):
        #    return False
        if not self.check_in_bounds(x, y):
            raise ValueError(f"Coordinates ({x}, {y}) are out of bounds.")
        if colour not in [1, 2]:
            raise ValueError(f"Invalid colour: {colour}. Must be 1 (black) or 2 (white).")
        if self.board[x,y] == 0:
            self.board[x,y] = colour
            return True
        return False
    
    def remove_stone(self, x, y):
        #if x not in range(self.size) and y not in range(self.size):
        #    return False
        if not self.check_in_bounds(x, y):
            raise ValueError(f"Coordinates ({x}, {y}) are out of bounds.")
        if self.board[x,y] != 0:
            self.board[x,y] = 0
            return True
        return False
    
    def liberties_check(self,x,y):
        #check the 4 directions. if neighbours are the other colour then -1 from liberties. If they are the same then add that stone to the group and search that stone's neighbours for liberties
        #currently just return liberties, but I'm not sure whether group should also be returned or something.
        #to handle overlapping liberties - maybe a visited hashmap.
        if not self.check_in_bounds(x, y):
            raise ValueError(f"Coordinates ({x}, {y}) are out of bounds.")
        
        liberties = 0
        group = {(x,y): True}
        visited = {}
        queue = deque(group)
        colour = self.board[x,y]
        opp = self.opposite_colour(colour)

        while queue:
            cx, cy = queue.popleft()
            for d in self.directions:
                dx, dy = self.directions[d]
                nx, ny = cx + dx, cy + dy
                ncoords = (nx,ny)
                if (nx < 0 or ny < 0  or 
                    nx == self.size or ny == self.size
                ):
                    continue
                          
                if self.board[nx,ny] == colour:
                    if ncoords not in group:
                        group[ncoords] = True
                        queue.append(ncoords)

                elif self.board[nx,ny] == opp:
                    continue
                
                else:
                    if ncoords not in visited:
                        liberties += 1
                        visited[(ncoords)] = True

        return liberties
    
    def opposite_colour(self, colour):
        if colour == 1:
            return 2
        elif colour == 2:
            return 1
        else:
            return 0
    #make groups of connected stones
    #check liberties of stones
    #
    #check if in atari
    #check if suicide move
    #check for repeated board state
    #figure out a basic gui
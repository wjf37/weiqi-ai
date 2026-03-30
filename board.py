import numpy as np
from collections import deque

class Board:
    def __init__(self, size=19):
        #colour 0 = empty colour 1 = black colour -1 = white
        self.size = size
        self.board = np.zeros((size, size), np.uint8)
        #parent stores the parent of each group placed aka the group id
        self.parent = {}
        #group_data stores the other stones and liberties left
        self.group_data = {}
        self.directions = {
            1: [0,1],
            2:[0,-1],
            3:[1,0],
            4:[-1,0]
        }

    def check_in_bounds(self, pos):
        if pos[0] in range(self.size) and pos[1] in range(self.size):
            return True
        return False
    
    def place_stone(self, pos, colour):
        x, y = pos
        if not self.check_in_bounds(x, y):
            raise ValueError(f"Coordinates ({x}, {y}) are out of bounds.")
        if colour not in [1, -1]:
            raise ValueError(f"Invalid colour: {colour}. Must be 1 (black) or -1 (white).")
        if self.board[x,y] != 0:
            raise ValueError(f"Coordinates ({x}, {y}) is already occupied.")
        else:
            self.board[x,y] = colour
            pos = (x,y)
            self.parent[pos] = pos
            liberties, enemies, friends = self.liberties_check(pos)
            
            if not liberties and not friends:
                return False
            
            new_group = {
                'stones': {pos},
                'size': 1,
                'liberties': liberties,
                'enemy_groups': enemies,
            }
            self.group_data[pos] = new_group

            #if there are friends, merge the groups
            for friend in friends:
                final_group = self.union(self.parent[pos], friend)
                
            #deal with enemies, check if they still have liberties left, and if not then remove group, then after removing the group run an update on the liberties and enemies for the neighbours.
            #for dealing with how the enemies handle the new group and or friends. 
            for enemy in enemies:
                enemy['liberties'] -= 1

    
    #change to remove group
    def remove_group(self, pos):
        x, y = pos
        if not self.check_in_bounds(x, y):
            raise ValueError(f"Coordinates ({x}, {y}) are out of bounds.")
        if self.board[x,y] != 0:
            self.board[x,y] = 0
            return True
        return False
    
    def liberties_check(self,pos):
        #with the changes to the group storage I'll have to change how liberties check works.
        #It should be cheaper since there won't be repeated calculations.
        #call liberties check in add stone so that groups can be merged.
        #union needs to be called in liberties check after all the liberties for the stone have been
        #calculated.
        #for remove group: do something like liberties check but for all neighbours so that liberties check
        #is called for them.
        x, y = pos
        if not self.check_in_bounds(x, y):
            raise ValueError(f"Coordinates ({x}, {y}) are out of bounds.")
    
        colour = self.board[x,y]
        opp = -colour

        liberties = set()
        enemies = set()
        friends = set()

        for d in self.directions:
            dx, dy = self.directions[d]
            nx, ny = x + dx, y + dy
            ncoords = (nx,ny)
            if (nx < 0 or ny < 0  or 
                nx == self.size or ny == self.size
            ):
                continue
            #this method gets called when placing a new stone so this new stone should get added to the group of the already existing stone          
            if self.board[nx,ny] == colour:
                friends.add(self.find_group((nx,ny)))

            elif self.board[nx,ny] == opp:
                enemies.add(self.find_group((nx,ny)))
            
            else:
                liberties.add((ncoords))
        
        return liberties, enemies, friends
    
    def find_group(self,pos):
        #when merging groups only the parent of the group needs to be updated
        if self.parent[pos] != pos:
            self.parent[pos] = self.find_group(self.parent[pos])
        return self.parent[pos]
    
    def union(self, pos1, pos2):
        #union by rank
        root1 = self.find_group(pos1)
        root2 = self.find_group(pos2)

        if root1 == root2:
            return
        if self.group_data[root1]['size'] < self.group_data[root2]['size']:
            root1, root2 = root2, root1

        self.parent[root2] = root1
        self.group_data[root1]['stones'].update(self.group_data[root2]['stones'])
        self.group_data[root1]['liberties'].update(self.group_data['liberties'])
        self.group_data[root1]['liberties'].difference_update(self.group_data[root2]['stones'])
        self.group_data[root1]['size'] = self.group_data[root1]['size'] + self.group_data[root2]['size']
        #handle enemy groups merging.
        shared_enemies = self.group_data[root1]['enemy_groups'] | self.group_data[root2]['enemy_groups']
        for enemy in shared_enemies:
            self.group_data[enemy]['enemy_groups'].discard(root2)
                

        del self.group_data[root2]
        
        return root1

    #
    #check if in atari
    #check if suicide move
    #check for repeated board state
    #figure out a basic gui
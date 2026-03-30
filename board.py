import numpy as np
from collections import deque

class Board:
    def __init__(self, size=19):
        #colour 0 = empty | colour 1 = black | colour -1 = white
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
        if pos[0] not in range(self.size) or pos[1] not in range(self.size):
            raise ValueError(f"Coordinates ({pos[0]}, {pos[1]}) are out of bounds.") 
    
    def place_stone(self, pos, colour):
        #place stone needs: legal check, suicide check, atari check (super atari check), kill check
        #sequence: input pos -> check neighbours -> legal check (suicide/ko) -> friendly merge check -> enemy group kill check
        self.check_in_bounds(self, pos)
        x, y = pos
        if colour not in [1, -1]:
            raise ValueError(f"Invalid colour: {colour}. Must be 1 (black) or -1 (white).")
        if self.board[x,y] != 0:
            raise ValueError(f"Coordinates ({x}, {y}) is already occupied.")
        else:
            self.board[x,y] = colour
            pos = (x,y)
            self.parent[pos] = pos
            liberties, enemies, friends = self.neighbours_check(pos)
            
            if not liberties and not friends:
                return False
            
 
            new_group = {
                'stones': {pos},  
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
    def remove_stones(self, pos):
        self.check_in_bounds(self, pos)
        x, y = pos
        if self.board[x,y] != 0:
            self.board[x,y] = 0
            return True
        return False

    def neighbours_check(self,pos):
        #get neighbouring positions status
        self.check_in_bounds(self, pos)
        x, y = pos
    
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
            if self.board[nx,ny] == colour:
                friends.add(self.find_group((nx,ny)))

            elif self.board[nx,ny] == opp:
                enemies.add(self.find_group((nx,ny)))
            
            else:
                liberties.add((ncoords))
        
        return liberties, enemies, friends
    

    def legal_check(self, pos, colour):
        pass
    
    def ko_check(self, pos, colour):
        pass

    def kill_check(self, pos, colour):
        pass


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
        
        self.parent[par2] = par1
        self.group_data[par1]['stones'].update(self.group_data[par2]['stones'])
        self.group_data[par1]['liberties'].update(self.group_data['liberties'])
        self.group_data[par1]['liberties'].difference_update(self.group_data[par2]['stones'])
        del self.group_data[par2]
        #to calculate the new liberties:
        #you have two groups that you need to combine as one. This one stone that gets placed need to have two neighbours of the same colour which belong to different groups.
        #I'm not sure where this check would go, whether the union function just carries out the union or maybe the liberties check handles the neighbours.
        #I think the new stone would get put into group 1 or somehing, and then union can be carried out and should calculate the correct liberties.
    
    def merge(self, pos, friends):
        #check if the stone has friends in diff groups, if so merge them into one group
        pass

    #make groups of connected stones
    #check liberties of stones
    #
    #check if in atari
    #check if suicide move
    #check for repeated board state
    #figure out a basic gui
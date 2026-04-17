'''
Currently used to store all of the game logic. 
Splitting it off into separate files might make more sense later
'''
import numpy as np

class Game:
    '''
    Contains all the game logic in relation to the board
    '''
    def __init__(self, size: int = 19) -> None:
        '''
        Initialises the basic necessities of the game such as:
        - board size,
        - constants used in the game logic,
        - storage for the groups of stones
        '''
        #colour 0 = empty | colour 1 = black | colour -1 = white
        self.size = size
        self.board = np.zeros((size, size), np.uint8)
        #parent stores the parent of each group placed aka the group id
        next_group_id: int = 0
        self.parent = {}
        #group_data stores the other stones and liberties left
        #group data format:
        self.group_data = {}
        self.directions = (
            [0,1],
            [0,-1],
            [1,0],
            [-1,0]
        )
        self.super_ko_counter: int = 0
        self.prev_game_state = self.board.copy()

    def check_in_bounds(self, pos: tuple[int, int]) -> None:
        '''
        Simple function to check that the coords are within
        the bounds of the board, if not then raise an error
        '''
        if pos[0] not in range(self.size) or pos[1] not in range(self.size):
            raise ValueError(f"Coordinates ({pos[0]}, {pos[1]}) are out of bounds.")

    def place_stone(self, pos: tuple[int, int], colour: int) -> None:
        '''
        Logic for placing a stone on the board, with error checking for
        illegal moves. Start of the sequence of checks and updates for placing a stone.
        '''
        #place stone needs: legal check, suicide check, atari check (super atari check), kill check
        #sequence: input pos -> check neighbours -> legal check (suicide/ko)
        #  -> friendly merge check -> enemy group kill check
        self.check_in_bounds(pos)
        x, y = pos
        if colour not in [1, -1]:
            raise ValueError(f"Invalid colour: {colour}. Must be 1 (black) or -1 (white).")
        if self.board[x,y] != 0:
            raise ValueError(f"Coordinates ({x}, {y}) is already occupied.")

        self.ko_check(pos, colour)

        self.board[x,y] = colour
        pos = (x,y)
        self.parent[pos] = pos
        liberties, enemies, friends = self.neighbours_check(pos)


        new_group = {
            'stones': {pos},
            'liberties': liberties,
            'enemy_groups': enemies,
        }
        self.group_data[pos] = new_group

        if not enemies and not friends:
            return

        #if there are friends, merge the groups
        for friend in friends:
            self.union(self.parent[pos], friend)

        #deal with enemies, check if they still have liberties left, and if not
        #then remove group, then after removing the group run an update on the
        #liberties and enemies for the neighbours.
        #for dealing with how the enemies handle the new group and or friends.
        for enemy in enemies:
            enemy['liberties'] -= 1


    #change to remove group
    def remove_stones(self, pos: tuple[int, int]) -> bool:
        '''
        Logic for removing a stone/group from the board
        '''
        # TODO: finish function
        self.check_in_bounds(pos)
        x, y = pos
        if self.board[x,y] != 0:
            self.board[x,y] = 0
            return True
        return False

    def neighbours_check(self, pos: tuple[int, int]):
        '''
        Used to check the neighbouring positions of a stone, to determine the liberties,
        and the enemy and friendly groups next to the stone and how they will be affected
        by the new stone.
        '''
        #get neighbouring positions status
        # TODO: Figure out structure of groups and explicitly type the return value
        self.check_in_bounds(pos)
        x, y = pos

        colour = self.board[x,y]
        opp = -colour

        liberties = set()
        enemies = set()
        friends = set()

        for dx, dy in self.directions:
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


    def ko_check(self, pos: tuple[int, int], colour: int) -> None:
        '''
        Checks that a move does not violate the ko rule
        '''
        new_board_state = self.board.copy()
        new_board_state[pos[0], pos[1]] = colour
        if new_board_state == self.prev_game_state:
            self.super_ko_counter += 1
            if self.super_ko_counter > 2:
                ##TODO: deal with superko/winning and losing the game later
                self.game_over(colour, False)
                raise ValueError("Current player loses due to repeated board state (super ko rule).")
            self.board = self.prev_game_state.copy()
            self.reset_turn()
            raise ValueError("You are not allowed to repeat the previous board state (ko rule).")
        pass

    def kill_check(self, pos: tuple[int, int], colour: int):
        '''
        Checks if the move kills any enemy groups to override the
        suicide rule
        '''
        pass

    def find_group(self,pos: tuple[int, int]):
        '''
        Finds the group to which a stone belongs to
        '''
        #when merging groups only the parent of the group needs to be updated
        if self.parent[pos] != pos:
            self.parent[pos] = self.find_group(self.parent[pos])
        return self.parent[pos]

    def union(self, pos1: tuple[int, int], pos2: tuple[int, int]):
        '''
        Unions two groups together
        '''
        #union by rank
        root1 = self.find_group(pos1)
        root2 = self.find_group(pos2)

        if root1 == root2:
            return
        group1 = self.group_data[root1]
        group2 = self.group_data[root2]

        if group1['size'] < group2['size']:
            root1, root2 = root2, root1

        self.parent[root2] = root1
        group1['stones'].update(group2['stones'])
        group1['liberties'].update(group2['liberties'])
        group1['liberties'].difference_update(group2['stones'])
        group1['size'] = group1['size'] + group2['size']
        #handle enemy groups merging.
        shared_enemies = group1['enemy_groups'] | group2['enemy_groups']
        for enemy in shared_enemies:
            self.group_data[enemy]['enemy_groups'].discard(root2)

        del self.group_data[root2]

        #to calculate the new liberties:
        #you have two groups that you need to combine as one.
        #This one stone that gets placed need to have two neighbours
        #of the same colour which belong to different groups.
        #I'm not sure where this check would go, whether the union function
        #just carries out the union or maybe the liberties check handles the neighbours.
        #I think the new stone would get put into group 1 or somehing, and then
        #union can be carried out and should calculate the correct liberties.
        
    def next_turn(self):
        '''
        Moves to the next turn
        '''
        pass

    def game_over(self, colour: int, isWinner: bool) -> None:
        '''
        Ends the game and declares the winner
        '''
        pass
    
    def reset_turn(self):
        '''
        Resets the turn to the previous state, used for undoing moves or handling illegal moves
        '''
        pass
    #make groups of connected stones
    #check liberties of stones
    #check if in atari
    #check if suicide move
    #check for repeated board state
    #figure out a basic gui

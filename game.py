'''
Currently used to store all of the game logic. 
Splitting it off into separate files might make more sense later
'''
import numpy as np
from dataclasses import dataclass

@dataclass
class GroupData:
    stones: set[tuple[int, int]]
    liberties: set[tuple[int, int]]
    enemy_groups: set[tuple[int, int]]

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
        #group_data stores the other stones and liberties left
        #group data format: set(parent: tuple[int,int], stones: set[tuple[int,int]], liberties: set[tuple[int,int]], enemy_groups: set[tuple[int,int]])
        self.groups: dict[tuple[int, int], GroupData] = {}
        self.stone_group_dict: dict[tuple[int, int], tuple[int, int]] = {}
        self.super_ko_counter: int = 0
        self.prev_game_state = self.board.copy()
    
    DIRECTIONS: tuple[tuple[int,int], ...] = (
        (0,1),
        (0,-1),
        (1,0),
        (-1,0)
    )

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

        new_stone: tuple[int, int] = pos

        self.ko_check(pos, colour)
        self.board[x,y] = colour
        liberties, enemies, friends, enemies_num = self.neighbours_check(pos)

        self.groups[pos] = (
            GroupData(stones={pos},
                      liberties=liberties,
                      enemy_groups=enemies
                    ))

        self.stone_group_dict[pos] = pos

        if not enemies and not friends:
            return

        #if there are friends, merge the groups
        for friend in friends:
            self.union(pos, friend, new_stone)

        #TODO: suicide check
        #required data: parent and group data for liberties of current group and the status of the enemies.
        #check if the current group has any liberties left with this move and if there are no liberties
        #then check for the liberties of the enemy groups that are neighbours. 
        


        #deal with enemies, check if they still have liberties left, and if not
        #then remove group, then after removing the group run an update on the
        #liberties and enemies for the neighbours.
        #for dealing with how the enemies handle the new group and or friends.


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

    def neighbours_check(self, pos: tuple[int, int]) -> tuple[set[tuple[int, int]], set[tuple[int, int]], set[tuple[int, int]], int]:
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
        #for the suicide check later to check if the stone being placed here is a
        #killing move
        enemies_num = 0

        for dx, dy in Game.DIRECTIONS:
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
                enemies_num += 1

            else:
                liberties.add((ncoords))

        return liberties, enemies, friends, enemies_num


    def ko_check(self, pos: tuple[int, int], colour: int) -> None:
        '''
        Checks that a move does not violate the ko rule y returning to the previous board state
        and also checks for super ko rule violation where the board state is repeated three times
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

    def suicide_check(self, pos: tuple[int, int], colour: int):
        '''
        Checks if the move takes all liberties of a group without killing an enemy group
        '''


    def kill_check(self, pos: tuple[int, int], colour: int):
        '''
        Checks if the move kills any enemy groups to override the
        suicide rule
        '''
        pass

    def find_group(self, pos: tuple[int, int]):
        '''
        Finds the group to which a stone belongs to
        '''
        #run initial search on the parents then go for a deeper search on the stones
        

    def union(self, pos1: tuple[int, int], pos2: tuple[int, int], new_stone: tuple[int, int]):
        '''
        Unions two groups together
        '''
        colour = self.board[pos1]
        #union by rank
        root1 = self.stone_group_dict[pos1]
        root2 = self.stone_group_dict[pos2]

        if root1 == root2:
            return
        group1 = self.groups[root1]
        group2 = self.groups[root2]

        if len(group1.stones) < len(group2.stones):
            root1, root2 = root2, root1

        #merge the properties of group 2 into group 1, making sure to calculate the new liberties accurately
        group1.stones.update(group2.stones)
        #TODO: double check liberties to make sure it is calculating properly
        #the only liberty that needs updating specifically is the last stone that was added
        group1.liberties.update(group2.liberties)
        group1.liberties.discard(new_stone)
        #handle enemy groups merging.
        shared_enemies = group1.enemy_groups | group2.enemy_groups
        for enemy in shared_enemies:
            self.groups[enemy].enemy_groups.discard(root2)

        del self.groups[root2]
    
    def update_group(self, parent: tuple[int, int]):
        '''
        Updates the group data for a given group, used after placing a stone or removing a group
        '''

    def next_turn(self):
        '''
        Moves to the next turn
        '''

    def game_over(self, colour: int, isWinner: bool) -> None:
        '''
        Ends the game and declares the winner
        '''
    
    def reset_turn(self):
        '''
        Resets the turn to the previous state, used for undoing moves or handling illegal moves
        '''
    #make groups of connected stones
    #check liberties of stones
    #check if in atari
    #check if suicide move
    #check for repeated board state
    #figure out a basic gui

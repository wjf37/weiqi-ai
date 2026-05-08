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
        self.check_in_bounds(pos)
        will_kill = False
        dead_groups = set(tuple[int, int])
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
            main_group = self.union(pos, friend, new_stone)

        for enemy in enemies:
            enemy_group = self.groups[enemy]
            enemy_group.enemy_groups.add(main_group)
            enemy_group.liberties.discard(pos)
            if enemy_group.liberties <= 0:
                will_kill = True
                dead_groups.add(enemy)

        self.pass_suicide_check(main_group, will_kill)
        #TODO: carry out remove stones on the enemy groups 

        #deal with enemies, check if they still have liberties left, and if not
        #then remove group, then after removing the group run an update on the
        #liberties and enemies for the neighbours.
        #for dealing with how the enemies handle the new group and or friends.


    #change to remove group
    def remove_stones(self, pos: tuple[int, int]):
        '''
        Logic for removing a group from the board + cleaup
        '''
        # TODO: finish function
        #set the stone positions in the group to 0
        #make a simpler liberties check function to refresh the liberties
        #of the killing groups
        #remove this group from enemy groups for the killing groups

        dead_group = self.groups[pos]
        for stone in dead_group.stones:
            self.board[stone] = 0
        
        groups_to_update = dead_group.enemy_groups
        for group in groups_to_update:
            self.groups[group].enemy_groups.discard(pos)
            self.update_liberties(group)
        del self.groups[pos]

    def neighbours_check(
            self,
            pos: tuple[int, int]
        ) -> tuple[
            set[tuple[int, int]],
            set[tuple[int, int]],
            set[tuple[int, int]],
            int
        ]:
        '''
        Used to check the neighbouring positions of a stone, to determine the liberties,
        and the enemy and friendly groups next to the stone and how they will be affected
        by the new stone.
        '''
        #get neighbouring positions status
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

    def pass_suicide_check(self, pos: tuple[int, int], will_kill: bool):
        '''
        Checks if the move takes all liberties of a group without killing an enemy group
        '''
        if self.groups[pos].liberties <= 0 and not will_kill:
            return False
        return True

    def find_group(self, pos: tuple[int, int]):
        '''
        Finds the group to which a stone belongs to
        '''
        #run initial search on the parents then go for a deeper search on the stones
        

    def union(self, pos1: tuple[int, int], pos2: tuple[int, int], new_stone: tuple[int, int]) -> tuple[int, int]:
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
        #the only liberty that needs updating specifically is the last stone that was added
        group1.liberties.update(group2.liberties)
        group1.liberties.discard(new_stone)
        #handle enemy groups merging.
        shared_enemies = group1.enemy_groups | group2.enemy_groups
        for enemy in shared_enemies:
            self.groups[enemy].enemy_groups.discard(root2)

        del self.groups[root2]

        return root1
    
    def update_liberties(self, pos: tuple[int, int]):
        '''
        Simple liberties updater for after a group is dead
        '''
        x, y = pos
        colour = self.board[x, y]
        opp = -colour
        cur_group = self.groups[pos]

        for dx, dy in Game.DIRECTIONS:
            nx, ny = x + dx, y + dy
            ncoords = (nx,ny)
            if (nx < 0 or ny < 0  or
                nx == self.size or ny == self.size
            ):
                continue

            if self.board[nx,ny] == 0:
                cur_group.liberties.add((ncoords))

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

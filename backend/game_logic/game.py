'''
Currently used to store all of the game logic. 
Splitting it off into separate files might make more sense later
'''
from enum import Enum, auto
from typing import List
import copy

from .groupdata import GroupData
from backend.game_logic import turn_logic as turn
from exceptions import MoveRejected


class GameState(Enum):
    ONGOING = auto()
    SCORE_COUNT = auto()
    FIN_RESIGN = auto()

DIRECTIONS: tuple[tuple[int,int], ...] = (
        (0,1),
        (0,-1),
        (1,0),
        (-1,0)
    )

class Game:
    '''
    Contains all the game logic in relation to the board
    '''
    def __init__(self, size: int = 19, komi: float = 6.5) -> None:
        '''
        Initialises the basic necessities of the game such as:
        - board size,
        - constants used in the game logic,
        - storage for the groups of stones
        '''
        #colour 0 = empty | colour 1 = black | colour -1 = white
        self.size = size
        self.komi = komi
        self.board = [[0 for i in range(size)] for j in range(size)]
        self.groups: dict[tuple[int, int], GroupData] = {}
        #for mapping stones to their group leader
        self.stone_group_dict: dict[tuple[int, int], tuple[int, int]] = {}
        self.super_ko_counter = 0
        self.white_score = 0
        self.black_score = 0
        self.pass_counter = 0
        self.current_player = 1
        self.turn_counter = 1
        self.turn_data: List[tuple[int, int, int]] = []
        self.state = GameState.ONGOING
        #stores the seen board states as a dict with a tuple of the 
        #board state and the player that made that state for both
        #situational and positional superko rules
        self.prev_states: dict[tuple[tuple[int, ...], ...], int] = {}

    @property
    def is_over(self) -> bool:
        '''
        Returns True if the game is over, False otherwise
        '''
        return self.state != GameState.ONGOING

    def board_to_tuple(self, board: list[list[int]]) -> tuple[tuple[int, ...], ...]:
        return tuple(tuple(row) for row in board)

    def place_stone(self, pos: tuple[int, int], colour: int) -> MoveRejected | None:
        '''
        Logic for placing a stone on the board, with error checking for
        illegal moves. Start of the sequence of checks and updates for placing a stone.
        '''
        if self.is_over:
            return MoveRejected.GAME_OVER
        prisoners = 0
        # Used to check if this turn will kill any enemy groups
        will_kill = False
        # Collect groups to kill this turn for easy removal and prisoner counting
        dead_groups: set[tuple[int, int]] = set()
        x, y = pos

        if x >= self.size or y >= self.size:
            return MoveRejected.OUT_OF_BOUNDS
        if colour not in [1, -1]:
            return MoveRejected.INVALID_COLOUR
            #raise ValueError(f"Invalid colour: {colour}. Must be 1 (black) or -1 (white).")
        if self.board[y][x] != 0:
            return MoveRejected.OCCUPIED_POINT
            #raise ValueError(f"Point({x}, {y}) is already occupied.")

        # Keep a copy of the stone being placed for updating the liberties later
        new_stone: tuple[int, int] = pos

        #temporary mutable board state, don't change original if move is illegal
        temp_board = copy.deepcopy(self.board)
        temp_groups = copy.deepcopy(self.groups)
        temp_sg_dict = copy.deepcopy(self.stone_group_dict)

        self.board[y][x] = colour
        liberties, enemies, friends = turn.neighbours_check(pos, temp_board, temp_sg_dict)

        temp_groups[pos] = (
            GroupData(stones={pos},
                        liberties=liberties,
                        enemy_groups=enemies
                    ))

        temp_sg_dict[pos] = pos

        #if there are friends, merge the groups
        main_group = pos
        for friend in friends:
            main_group = turn.union(pos, friend, new_stone, temp_groups, temp_sg_dict)

        for enemy in enemies:
            enemy_group = temp_groups[enemy]
            enemy_group.enemy_groups.add(main_group)
            enemy_group.liberties.discard(pos)
            if len(enemy_group.liberties) <= 0:
                will_kill = True
                dead_groups.add(enemy)

        for group in dead_groups:
            prisoners += turn.remove_stones(group, temp_board, temp_groups)

        new_state = self.board_to_tuple(temp_board)

        #if ko check does not pass then send exception
        if turn.is_pos_ko(self.prev_states, new_state):
            return MoveRejected.KO
            #raise IllegalMoveError("This move violates the ko rule. You must play elsewhere or pass first.")

        #if suicide check does not pass send exception
        if not turn.is_suicide(main_group, will_kill, temp_groups):
            return MoveRejected.SUICIDE
            #raise IllegalMoveError("This move violates the suicide rule. You must play elsewhere or pass first.")
        
        #only reach this point when the moves are not found to be illegal
        self.board = copy.deepcopy(temp_board)
        self.groups = copy.deepcopy(temp_groups)
        self.stone_group_dict = copy.deepcopy(temp_sg_dict)

        #add the successful move to game history with the player who made it for situational ko checks 
        self.prev_states[new_state] = colour

        if colour == 1:
            self.black_score += prisoners
        else:
            self.white_score += prisoners

        turn_value = (x, y, colour)
        self.turn_data.append(turn_value)
        self.current_player = -self.current_player
        self.turn_counter += 1
        self.pass_counter = 0


    def check_in_bounds(self, pos: tuple[int, int]) -> None:
        '''
        Simple function to check that the coords are within
        the bounds of the board, if not then raise an error
        '''
        if pos[0] not in range(self.size) or pos[1] not in range(self.size):
            raise ValueError(f"Point ({pos[0]}, {pos[1]}) is out of bounds.")

    def resign(self, colour: int) -> None:
        '''
        Ends the game, makes the other player the winner
        '''
        self.game_over(-colour)
        self.state = GameState.FIN_RESIGN

    def reset_turn(self, temp_board, temp_groups, temp_sg_dict) -> None:
        '''
        Resets the turn to the previous state, used for undoing moves or handling illegal moves
        '''
        self.board = temp_board
        self.groups = temp_groups
        self.stone_group_dict = temp_sg_dict

    def pass_turn(self) -> None:
        '''
        Handles the logic for passing a turn, including checking for consecutive passes to end the game
        '''
        self.prev_game_state = self.board.copy()
        self.pass_counter += 1
        if self.pass_counter >= 2:
            self.state = GameState.SCORE_COUNT 
            self.calculate_score_ja()

    def calculate_score_ja(self) -> None:
        '''
        Calculates the score for both players at the end of the game using Japanese scoring,
        including territory and prisoners
        '''
        seen_points: set[tuple[int, int]] = set()
        for x in range(self.size):
            for y in range(self.size):
                pos = (x, y)
                if pos not in seen_points and self.board[y][x] == 0:
                    empty, boundaries = self.flood_fill(x, y)
                    if boundaries == (True, False):
                        self.black_score += len(empty)
                    elif boundaries == (False, True):
                        self.white_score += len(empty)
                    elif boundaries == (True, True):
                        # Disputed territory, handle accordingly (e.g., allow players to mark dead stones)
                        #self.dead_stone_dispute()
                        pass
                    seen_points.update(empty)
        #for end of game clear territory calculation

    def flood_fill(self, x: int, y: int) -> tuple[set[tuple[int, int]], tuple[bool, bool]]:
        '''
        Flood fill algorithm to determine the territory controlled by a player.
        Returns a set of positions that are part of the territory and a tuple indicating boundary colors.
        '''
        pos = (x, y)
        seen: set[tuple[int, int]] = set()
        empty: set[tuple[int, int]] = set()
        stack: list[tuple[int, int]] = [pos]
        boundaries = (False, False)  # (has_black_boundary, has_white_boundary)
        groups: set[tuple[int, int]] = set()
        seen.add(pos)

        while stack:
            current = stack.pop()
            cur_x, cur_y = current
            if self.board[cur_x][cur_y] == 0:
                empty.add(current)
                for dx, dy in DIRECTIONS:
                    neighbour = (cur_x + dx, cur_y + dy)
                    if neighbour not in seen and 0 <= neighbour[0] < self.size and 0 <= neighbour[1] < self.size:
                        stack.append(neighbour)
                        seen.add(neighbour)

            else:
                if self.board[cur_y][cur_x] == 1:
                    boundaries = (True, boundaries[1])
                    groups.add(self.stone_group_dict[current])
                elif self.board[cur_y][cur_x] == -1:
                    boundaries = (boundaries[0], True)
                    groups.add(self.stone_group_dict[current])

        return empty, boundaries
    
    def dead_stone_dispute(self, groups: set[tuple[int, int]]) -> None:
        '''
        When the flood fill finds a territory occupied by both players,
        it lets the players mark which stones are dead and which are alive.
        '''
        # highlight the disputed groups and change ui element to allow for agreeing
        # whether a group is dead or not


    def game_over(self, winner: int) -> None:
        '''
        Ends the game, calculates score and declares the winner. Saves the turn data.
        ''' 
    
    def review(self) -> None:
        '''
        Allows for reviewing the game after it has ended, using the stored turn data
        '''
    

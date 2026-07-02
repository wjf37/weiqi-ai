'''
Currently used to store all of the game logic. 
Splitting it off into separate files might make more sense later
'''
from enum import Enum, auto
from typing import List

import numpy as np
from dataclasses import dataclass
from turn_logic import PlayTurn

@dataclass
class GroupData:
    stones: set[tuple[int, int]]
    liberties: set[tuple[int, int]]
    enemy_groups: set[tuple[int, int]]

class GameState(Enum):
    ONGOING = auto()
    FIN_SCORE = auto()
    FIN_RESIGN = auto()

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
        self.board = [[0 for i in range(size)] for j in range(size)]
        self.groups: dict[tuple[int, int], GroupData] = {}
        self.stone_group_dict: dict[tuple[int, int], tuple[int, int]] = {}
        self.super_ko_counter = 0
        self.prev_game_state = self.board.copy()
        self.white_score = 0
        self.black_score = 0
        self.pass_counter = 0
        self.current_player = 1
        self.turn_counter = 1
        #turn data == pos, colour
        self.turn_data: List[tuple[int, int, int]] = []
        self.state = GameState.ONGOING

    @property
    def is_over(self) -> bool:
        '''
        Returns True if the game is over, False otherwise
        '''
        return self.state != GameState.ONGOING
    
    def place_stone(self, pos: tuple[int, int], colour: int) -> None:
        '''
        Logic for placing a stone on the board, with error checking for
        illegal moves. Start of the sequence of checks and updates for placing a stone.
        '''
        if self.is_over:
            raise ValueError("Game is over, cannot place stone.")
        prisoners = 0
        # Used to check if this turn will kill any enemy groups
        will_kill = False
        # Collect groups to kill this turn for easy removal and prisoner counting
        dead_groups = set(tuple[int, int])
        prisoners = 0
        x, y = pos

        if colour not in [1, -1]:
            raise ValueError(f"Invalid colour: {colour}. Must be 1 (black) or -1 (white).")
        if self.board[x,y] != 0:
            raise ValueError(f"Point({x}, {y}) is already occupied.")

        # Keep a copy of the stone being placed for updating the liberties later
        new_stone: tuple[int, int] = pos

        turn = PlayTurn(self.board, self.groups, self.stone_group_dict)

        if turn.ko_check():
            self.super_ko_counter += 1
            if self.super_ko_counter >= 3:
                self.resign(colour)
                raise ValueError("Current player loses due to repeated board state (super ko rule).")
            self.reset_turn()

        self.board[x,y] = colour
        liberties, enemies, friends = turn.neighbours_check()

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
            main_group = turn.union(pos, friend, new_stone)

        for enemy in enemies:
            enemy_group = self.groups[enemy]
            enemy_group.enemy_groups.add(main_group)
            enemy_group.liberties.discard(pos)
            if enemy_group.liberties <= 0:
                will_kill = True
                dead_groups.add(enemy)

        if not turn.pass_suicide_check(main_group, will_kill):
            self.reset_turn()
        for group in dead_groups:
            prisoners += self.remove_stones(group)
        if colour == 1:
            self.black_score += prisoners
        else:
            self.white_score += prisoners

        self.prev_game_state = self.board.copy()

        self.board, self.groups, self.stone_group_dict = turn.return_values()
        self.turn_data.append((pos, colour))

    def check_in_bounds(self, pos: tuple[int, int]) -> None:
        '''
        Simple function to check that the coords are within
        the bounds of the board, if not then raise an error
        '''
        if pos[0] not in range(self.size) or pos[1] not in range(self.size):
            raise ValueError(f"Point ({pos[0]}, {pos[1]}) is out of bounds.")

    def next_turn(self) -> None:
        '''
        Moves to the next turn.
        '''
        self.current_player = -self.current_player
        self.turn_counter += 1
        self.pass_counter = 0
        self.super_ko_counter = 0

    def resign(self, colour: int) -> None:
        '''
        Ends the game, makes the other player the winner
        '''
        self.game_over(-colour)
        self.state = GameState.FIN_RESIGN

    def reset_turn(self) -> None:
        '''
        Resets the turn to the previous state, used for undoing moves or handling illegal moves
        '''
        self.board = self.prev_game_state.copy()

    def pass_turn(self) -> None:
        '''
        Handles the logic for passing a turn, including checking for consecutive passes to end the game
        '''
        turn = PlayTurn(self.board, None, None)
        self.prev_game_state = self.board.copy()
        self.pass_counter += 1
        if self.pass_counter >= 2:
            self.state = GameState.FINISHED_SCORE 
            self.calculate_score()

    def calculate_score(self) -> None:
        '''
        Calculates the score for both players at the end of the game, including territory and prisoners
        '''

    def game_over(self, winner: int) -> None:
        '''
        Ends the game, calculates score and declares the winner. Saves the turn data.
        '''
    
    def review(self) -> None:
        '''
        Allows for reviewing the game after it has ended, using the stored turn data
        '''
'''
All the methods used in the turn logic of the game.
'''
from dataclasses import dataclass

@dataclass
class GroupData:
    stones: set[tuple[int, int]]
    liberties: set[tuple[int, int]]
    enemy_groups: set[tuple[int, int]]

DIRECTIONS: tuple[tuple[int,int], ...] = (
        (0,1),
        (0,-1),
        (1,0),
        (-1,0)
    )
class PlayTurn:
    def __init__(self,
                 board: list[list[int]],
                 groups: dict[tuple[int, int], GroupData],
                 stone_group_dict: dict[tuple[int, int], tuple[int, int]],
                ):
        self.board = board
        self.groups = groups
        self.stone_group_dict = stone_group_dict

    def remove_stones(self, pos: tuple[int, int]) -> int:
        '''
        Logic for removing a group from the board + cleaup
        '''
        dead_group = self.groups[pos]
        prisoners = len(dead_group.stones)
        for stone in dead_group.stones:
            self.board[stone] = 0
        
        groups_to_update = dead_group.enemy_groups
        for group in groups_to_update:
            self.groups[group].enemy_groups.discard(pos)
            self.update_liberties(group)
        del self.groups[pos]
        return prisoners

    def neighbours_check(
            self,
            pos: tuple[int, int],z
        ) -> tuple[
            set[tuple[int, int]],
            set[tuple[int, int]],
            set[tuple[int, int]]
        ]:
        '''
        Used to check the neighbouring positions of a stone, to determine the liberties,
        and the enemy and friendly groups next to the stone and how they will be affected
        by the new stone.
        '''
        #get neighbouring positions status
        size = len(self.board)
        x, y = pos
        
        colour = self.board[x][y]
        opp = -colour

        liberties = set(tuple[int, int])
        enemies = set(tuple[int, int])
        friends = set(tuple[int, int])

        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            ncoords = (nx,ny)
            if (nx < 0 or ny < 0  or
                nx == size or ny == size
            ):
                continue
            if self.board[nx][ny] == colour:
                friends.add(self.stone_group_dict[(nx,ny)])
            elif self.board[nx][ny] == opp:
                enemies.add(self.stone_group_dict[(nx,ny)])
            else:
                liberties.add((ncoords))

        return liberties, enemies, friends


    def ko_check(self, pos: tuple[int, int], colour: int) -> bool:
        '''
        Checks that a move does not violate the ko rule y returning to the previous board state
        and also checks for super ko rule violation where the board state is repeated three times
        '''
        prev_board_state = self.board.copy()
        new_board_state = [row[:] for row in self.board]  # Create a copy of the board
        new_board_state[pos[0], pos[1]] = colour
        if new_board_state == prev_board_state:
            return True
        return False

    def pass_suicide_check(self, pos: tuple[int, int], will_kill: bool) -> bool:
        '''
        Checks if the move takes all liberties of a group without killing an enemy group
        '''
        if self.groups[pos].liberties <= 0 and not will_kill:
            return False
        return True

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

    def update_liberties(self, pos: tuple[int, int]) -> None:
        '''
        Simple liberties updater for after a group is dead
        '''
        x, y = pos
        cur_group = self.groups[pos]

        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            ncoords = (nx,ny)
            if (nx < 0 or ny < 0  or
                nx == self.size or ny == self.size
            ):
                continue

            if self.board[nx,ny] == 0:
                cur_group.liberties.add((ncoords))

    def return_values(self):
        return self.board, self.groups, self.stone_group_dict
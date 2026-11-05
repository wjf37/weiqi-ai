from dataclasses import dataclass

@dataclass
class GroupData:
    stones: set[tuple[int, int]]
    liberties: set[tuple[int, int]]
    enemy_groups: set[tuple[int, int]]
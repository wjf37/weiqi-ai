'''
All the methods used in the turn logic of the game.
'''
from .groupdata import GroupData

DIRECTIONS: tuple[tuple[int,int], ...] = (
        (0,1),
        (0,-1),
        (1,0),
        (-1,0)
    )

def remove_stones(
    pos: tuple[int,int],
    board: list[list[int]],
    groups: dict[tuple[int,int], GroupData]
) -> int:
    '''
    Logic for removing a group from the board + cleaup.
    Returns number of prisoners gained
    '''
    dead_group = groups[pos]
    prisoners = len(dead_group.stones)
    for x, y in dead_group.stones:
        board[y][x] = 0
    
    groups_to_update = dead_group.enemy_groups
    for group in groups_to_update:
        groups[group].enemy_groups.discard(pos)
        update_liberties(group, board, groups)
    del groups[pos]
    return prisoners

def neighbours_check(
    pos: tuple[int, int],
    board: list[list[int]],
    sg_dict: dict[tuple[int,int], tuple[int,int]]
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
    size = len(board)
    x, y = pos
    
    colour = board[y][x]
    opp = -colour

    liberties: set[tuple[int, int]] = set()
    enemies: set[tuple[int, int]] = set()
    friends: set[tuple[int, int]] = set()

    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        ncoords = (nx,ny)
        if (nx < 0 or ny < 0  or
            nx == size or ny == size
        ):
            continue
        if board[ny][nx] == colour:
            friends.add(sg_dict[(nx,ny)])
        elif board[ny][nx] == opp:
            enemies.add(sg_dict[(nx,ny)])
        else:
            liberties.add((ncoords))

    return liberties, enemies, friends


def is_pos_ko(
    prev_states: dict[tuple[tuple[int, ...], ...], int],
    new_state: tuple[tuple[int, ...], ...]
) -> bool:
    '''
    Checks that a move does not violate the positional super ko rule by checking
    the board state post move against all past board states
    '''
    if new_state in prev_states:
        return True
    return False

def is_sit_ko(
    colour: int,
    prev_states: dict[tuple[tuple[int, ...], ...], int],
    new_state: tuple[tuple[int, ...], ...]
) -> bool:
    '''
    Checks that a move does not violate the situational super ko rule by checking
    the board state post move against all past board states then checking if it 
    was by the same player
    '''
    player = prev_states.get(new_state, 0)
    return colour == player

def is_suicide(
    pos: tuple[int,int],
    will_kill: bool,
    groups: dict[tuple[int,int], GroupData]
) -> bool:
    '''
    Checks if the move removes all liberties of its group without killing an enemy group
    '''
    if len(groups[pos].liberties) <= 0 and not will_kill:
        return True
    return False

def union(
    pos1: tuple[int, int],
    pos2: tuple[int, int],
    new_stone: tuple[int, int],
    groups: dict[tuple[int,int], GroupData],
    sg_dict: dict[tuple[int,int], tuple[int,int]]
) -> tuple[int, int]:
    '''
    Unions two groups together using the largest group as the head
    '''
    #union by rank
    root1 = sg_dict[pos1]
    root2 = sg_dict[pos2]

    if root1 == root2:
        return root1
    group1 = groups[root1]
    group2 = groups[root2]

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
        groups[enemy].enemy_groups.discard(root2)

    del groups[root2]

    return root1

def update_liberties(
    pos: tuple[int, int],
    board: list[list[int]],
    groups: dict[tuple[int,int], GroupData]    
) -> None:
    '''
    Simple liberties updater for after a group is dead
    '''
    x, y = pos
    cur_group = groups[pos]
    size = len(board)
    for dx, dy in DIRECTIONS:
        nx, ny = x + dx, y + dy
        ncoords = (nx,ny)
        if (nx < 0 or ny < 0  or
            nx == size or ny == size
        ):
            continue

        if board[ny][nx] == 0:
            cur_group.liberties.add((ncoords))

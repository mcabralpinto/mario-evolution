
# Evolved Mario Controller


def corre(action, landscape, enemies, can_jump, on_ground, Mario, Sprite, mario_pos, **kwargs):


    action[Mario.KEY_RIGHT] = 1
    

    is_hole = all(landscape[y, 11] == 0 for y in range(12, 22)) or \
              all(landscape[y, 12] == 0 for y in range(12, 22))

    solids = [-10, 16, 20, 21]
    is_wall = any(landscape[x, y] in solids for x in range(10, 13) for y in range(10, 13)) 

    enemy_types = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

    print(f"Enemies: {enemies}. ")
    
    enemies_exist = enemies and any(
        (ek in enemy_types)
        and (abs(ex - mario_pos[0]) <= 30.0)
        for ek, ex, ey in enemies
    )

    for ek, ex, ey in enemies or []:
        if ek in enemy_types:
            print(f"Enemy detected: {ek} at ({ex}, {ey})")
            print(f"absolute Mario.x position: {abs(ex - mario_pos[0])}. ")
            print(f"absolute Mario.y position: {abs(ey - mario_pos[1])}. ")

    if (is_hole or is_wall or enemies_exist):
        action[Mario.KEY_JUMP] = 1
        action[Mario.KEY_SPEED] = 0

         


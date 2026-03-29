
# Evolved Mario Controller

def corre(action, landscape, enemies, can_jump, on_ground, Mario, Sprite, mario_pos, **kwargs):
    #print("Landscape:\n", landscape[9:12, 11:14])

    is_hole = all(landscape[y, 12] == 0 for y in range(12, 22)) or \
              all(landscape[y, 13] == 0 for y in range(12, 22))

    solids = [-10, 16, 20, 21]
    is_wall = any(landscape[x, y] in solids for y in range(11, 14) for x in range(9, 12)) 

    enemy_types = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]

    # print(f"Enemies: {enemies}. ")
    
    enemies_ahead = enemies and any(
        (ek in enemy_types)
        and (ex - mario_pos[0] <= 30.0)
        for ek, ex, ey in enemies
    )

    # for ek, ex, ey in enemies or []:
    #     if ek in enemy_types:
    #         print(f"Enemy detected: {ek} at ({ex}, {ey})")
    #         print(f"absolute Mario.x position: {abs(ex - mario_pos[0])}. ")
    #         print(f"absolute Mario.y position: {abs(ey - mario_pos[1])}. ")

    action[Mario.KEY_RIGHT] = 1
    # if not on_ground:
    #     action[Mario.KEY_JUMP] = 1
    # else:
    #     if (is_hole or is_wall or enemies_ahead) and can_jump:
    #             action[Mario.KEY_JUMP] = 1
        # action[Mario.KEY_RIGHT] = 0
    # elif on_ground or can_jump:
    #     action[Mario.KEY_JUMP] = 0
    #     action[Mario.KEY_JUMP] = 0
    #     action[Mario.KEY_RIGHT] = 1
    # print(is_hole, is_wall, enemies_ahead, can_jump, on_ground, action)

         


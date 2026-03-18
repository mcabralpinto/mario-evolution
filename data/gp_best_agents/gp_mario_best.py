
# Evolved Mario Controller (Random Search)
# Fitness: 0.0

def corre(action, landscape, enemies, can_jump, on_ground, Mario, Sprite, **kwargs):
    if (not ((can_jump and ((can_jump and on_ground) or obstacle_ahead)) and (enemy_near and (not (not enemy_near))))):
        if (enemy_near and ((not (not enemy_near)) or (not (not can_jump)))):
            action[Mario.KEY_LEFT] = int(False)
            action[Mario.KEY_JUMP] = int(False)
            pass

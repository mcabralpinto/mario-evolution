
# Evolved Mario Controller
# Fitness: 3889.2000378280068


def corre(action, landscape, enemies, can_jump, on_ground, Mario, Sprite, **kwargs):
    # --- SENSORS & HEURISTICS ---
    
    # 1. ENEMY RADAR
    # Categorize enemies by relative position to Mario
    enemy_near = any(abs(ex) < 40 and abs(ey) < 40 for ex, ey, ek in enemies)
    enemy_ahead = any(0 < ex < 50 and abs(ey) < 20 for ex, ey, ek in enemies)
    enemy_above = any(abs(ex) < 20 and -40 < ey < -5 for ex, ey, ek in enemies)
    enemy_behind = any(-40 < ex < 0 and abs(ey) < 20 for ex, ey, ek in enemies)

    # 2. LANDSCAPE ANALYZER
    wall_ahead = False
    obstacle_ahead = False
    hole_ahead = False
    slope_ahead = False
    
    if landscape is not None:
        # Mario is centered at roughly [11, 11] in the 22x22 grid
        # wall_tiles usually: -10 (border), 16, 20, 21 (bricks/blocks)
        wall_tiles = (-10, 16, 20, 21)
        
        # Check for vertical obstacles (walls) 1 or 2 blocks ahead
        wall_ahead = any(landscape[row, 12] in wall_tiles for row in range(9, 12)) or                      any(landscape[row, 13] in wall_tiles for row in range(9, 12))
        
        # Check for low obstacles (pipes/steps) Mario can jump over
        obstacle_ahead = landscape[11, 12] != 0 or landscape[11, 13] != 0
        
        # Check for slopes (is the ground rising?)
        slope_ahead = landscape[10, 12] != 0
        
        # Check for floor gaps (Holes)
        # Scan 1 to 4 tiles ahead at Mario's feet level
        hole_ahead = True
        for x_off in range(12, 16): 
            if landscape[12, x_off] != 0 or landscape[13, x_off] != 0:
                hole_ahead = False
                break

    # 3. STATE AGGREGATION
    # A general "Danger" flag if a jump is likely the only solution
    danger_ahead = hole_ahead or wall_ahead or enemy_ahead

    # 4. SAFE DEFAULT POLICY
    action[Mario.KEY_RIGHT] = int(True)
    if danger_ahead and can_jump:
        action[Mario.KEY_JUMP] = int(True)
    if enemy_near:
        action[Mario.KEY_SPEED] = int(True)
    
    # INDIVIDUAL GENERATED CODE vvv

    for _ in range(64):
        if not ((on_ground and (obstacle_ahead and enemy_above))):
            break
        for _ in range(64):
            if not (((enemy_behind and ((not ((enemy_behind and ((not (not (not can_jump))) or can_jump)) or danger_ahead)) or (enemy_behind or enemy_above))) or danger_ahead)):
                break
            pass
    if slope_ahead:
        pass


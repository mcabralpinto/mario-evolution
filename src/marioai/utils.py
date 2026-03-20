import numpy


__all__ = ['extractObservation', 'Observation']


def _parse_bool_token(token):
    return token == "true"

class Observation(object):
    """
    Structured observation data from the environment.
    """
    def __init__(self, may_jump=False, on_ground=False, mario_pos=None, enemies=None, 
                 level_scene=None, status=0, distance=0.0, time_left=0, mario_mode=0, coins=0):
        self.may_jump = may_jump
        self.on_ground = on_ground
        self.mario_pos = mario_pos
        self.enemies = enemies if enemies is not None else []
        self.level_scene = level_scene
        self.status = status
        self.distance = distance
        self.time_left = time_left
        self.mario_mode = mario_mode
        self.coins = coins

    def __repr__(self):
        return (f"Observation(may_jump={self.may_jump}, on_ground={self.on_ground}, "
                f"mario_pos={self.mario_pos}, enemies_len={len(self.enemies) if self.enemies else 0}, "
                f"status={self.status}, distance={self.distance})")

powsof2 = (1, 2, 4, 8, 16, 32, 64, 128,
                         256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072)

def decode(estate):
    """
    decodes the encoded state estate, which is a string of 61 chars
    """
    dstate = numpy.empty(shape = (22, 22), dtype = numpy.int32)
    for i in range(22):
        for j in range(22):
            dstate[i, j] = 2
    row = 0
    col = 0
    totalBitsDecoded = 0
    reqSize = 31
    assert len(estate) == reqSize, "Error in data size given %d! Required: %d \n data: %s " % (len(estate), reqSize, estate)
    
    for i in range(len(estate)):
        cur_char = estate[i]
        
        for j in range(16):
            totalBitsDecoded += 1
            if (col > 21):
                row += 1
                col = 0
            if ((int(powsof2[j]) & int(ord(cur_char))) != 0):
                dstate[row, col] = 1
            else:
                dstate[row, col] = 0
            col += 1
            if (totalBitsDecoded == 484):
                break
    return dstate

def extractObservation(data):
    """
    Parses the array of strings and returns an Observation namedtuple.
    """
    if isinstance(data, bytes):
        data = data.decode()
    # Handle fast TCP 'E' message (Merged observation)
    if data[0] == 'E':
        mayMarioJump = _parse_bool_token(data[1])
        isMarioOnGround = _parse_bool_token(data[2])
        levelScene = decode(data[3:34])
        # data[34:] checks sum but we can skip strict check for speed or implement if needed
        return Observation(may_jump=mayMarioJump, on_ground=isMarioOnGround, level_scene=levelScene)

    parts = data.split(' ')
    if parts[0] == 'FIT':
        status = int(parts[1])
        distance = float(parts[2])
        timeLeft = int(parts[3])
        marioMode = int(parts[4])
        coins = int(parts[5])
        # specific handling for fitness packet
        return Observation(status=status, distance=distance, time_left=timeLeft, mario_mode=marioMode, coins=coins)

    elif parts[0] == 'O':
        mayMarioJump = _parse_bool_token(parts[1])
        isMarioOnGround = _parse_bool_token(parts[2])
        
        # Parse Level Scene (22x22 flattened)
        # However, 'O' message format in original MarioAI is usually:
        # [O, mayJump, onGround, ...grid..., marioX, marioY, ...enemies...]
        # The original code looped 484 times.
        
        levelScene = numpy.empty(shape=(22, 22), dtype=numpy.int32)
        k = 0
        current_idx = 3
        for i in range(22):
            for j in range(22):
                levelScene[i, j] = int(parts[current_idx])
                current_idx += 1
        
        marioFloats = (float(parts[487]), float(parts[488]))
        
        # k += 2 -> 489
        current_idx = 489
        enemiesFloats = []
        while current_idx < len(parts):
             # basic protection against empty strings at the end
            if parts[current_idx]:
                enemiesFloats.append(float(parts[current_idx]))
            current_idx += 1

        enemiesFloats = [ (enemiesFloats[i], enemiesFloats[i+1], enemiesFloats[i+2]) for i in range(0, len(enemiesFloats), 3) ]
        
        distance = marioFloats[0]

        return Observation(may_jump=mayMarioJump, 
                           on_ground=isMarioOnGround, 
                           mario_pos=marioFloats, 
                           enemies=enemiesFloats, 
                           level_scene=levelScene,
                           distance=distance)

    else:
        # Fallback or error
        # print("Unknown data format:", data)
        return Observation()

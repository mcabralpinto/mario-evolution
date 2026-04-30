# GRAMMAR

- pass (added initially)
    - penalize pass amount of times it appears in the code?
    - just remove "pass"es (to explore search space more effetively). needed to make some changes to coode

- auxiliary perceptions (hole/obstacle/enemy ahead)

- simpler versions of past perceptions (28/3)
    - tweaked (29 - 31/3)
    - added drop and enemy above detection (31/3)
    - readujsted to those requested in project statement 
    - some stuff like position values tampered with (explain better in the report!)

# FITNESS

- stuck (27/3)
    - stuck penalty (not good enough)
    - stuck penalty proportional to stuck time - now he's jumping!

- always jumping (28/3) 
    - discount air time - too punitive! marios don't learn to jump.
    - curriculum (good results. passes 2 levels)
    - curriculum adjustments! (50% -> 10% -> 20%)
    - revert to old and try to get values right (11/4) (10 -> 50)
    - different values (1 -> 10 -> 25 -> 70 -> 150 -> 50) (we can kind of conclude that this alone isn't going to help. we need to either find a better way of enforcing our wished behavior or simply accept running and jumping with minor optimizations as the best solution)

- penalize closeness to enemies (later removed, i don't remember why)

- bloat control (1/4)
    - reduce (7/4)
    - change to the library version with 2 tournaments (10/4)

- overhaul stuck penalty - now only when truly stuck and not waiting (19/4)
- simple enemy penalty - similar to what we had before (19/4)

- kill detection function (explain below) (28/4)
    - mention old function (at the end of document) and current one (in the hunter.py func)

# MISC

- added to observation/fit function
    - distance! (initially)
    - current generation (for scheduling)

- mencionar chatice do jump (é preciso tirar e voltar a por!)

- remove break (29/3) -> made model more generalizeable 

- mutation / crossover probabilities (29/3)
    - increased crossover (0.9, 0.3) -> probably caused too little genetic variety
    - balanced (0.5, 0.5) (30/3)

- elitism (29/3)
    - removed, but later re-added

- increase episodes! (28/3)
    - refactor to 3 seeds, 5 difficulties (29/3)
    - refactor to 5 seeds, 3 difficulties (30/3)
    - try random 5 seeds (31/3) -> some marios get lucky! we need a better way to measure (mention: we were making the mistake of having different seeds within the same generation - fitnesses must be comparable!)
    - each M generations, a pool of N seeds, equal within a generation (5/4) -> good generalization (200gen/200pop)! but still only passing around 2-3 levels. we need to make the marios more consistent: make them start at low difficulty and go to high difficulty as time progresses, maybe?
    - dynamic difficulty window (6/4)
        - possible refinement: heavier weighting of harder levels in the window
        - other: give more time to harder windows
    - teacher said we only need 3 difs we're now not using dynamic and training on the 3 diffs (later).
    - mencionar tentar a rotação de seeds com mais seeds mas isso aumentar muito o tempo de treino para gains superficiais
    - now doing 300gen/200pop (18/4)
    - seed rotation (original: every 10 seeds) (22/04)
        - every 5 seeds: worse results! (see why)
        - every 20 seeds: worse results! (see why)
        - every 10 seeds: bad result! leads to next point
    - get checkpoint at each seed new seed insertion; evaluate best at end (26/04)
        - results show stagnation after first good result. 200 gens is probably enough at a budget.
    - attempt 100 instead of 200pop (29/04) -> comparable results! start using 100 pop

- checkpoints

# OTHER

    - melhorámos o script de teste original (duas opções)

# TRY

- coin reward

- different max tree heights
    - mutation subtree!

- penalize high speeds
    - make a reward that is constant every time he moves forward (don't encourage high velocity)

- apply random waits at the start to make enemy timing less predictable, thus forcing better generalization

- evolutionary strategies

- add any/all/for to grammar?




### old detection (simple heuristic)

    def enemies_in_radius(self, obs, radius):
        e = []
        for enemie in obs.enemies:
            if enemie[0] != 2:
                continue
            if abs(enemie[1] - obs.mario_pos[0]) <= radius:
                print(abs(enemie[1] - obs.mario_pos[0]))
                e.append(enemie)
        return e

        if last_obs:
            print("last danger zone")
            last_danger_zone = self.enemies_in_radius(last_obs, small_x_radius)
            print("current danger zone")
            danger_zone = self.enemies_in_radius(current_obs, small_x_radius)
            print("current big radius enemies")
            big_radius_enemies = self.enemies_in_radius(current_obs, big_x_radius) 
            print("last big radius enemies")
            last_big_radius_enemies = self.enemies_in_radius(last_obs, big_x_radius) 
            # count kills
            if len(danger_zone) < len(last_danger_zone) and len(big_radius_enemies) < len(last_big_radius_enemies):
                # if there are fewer enemies in the small radius and also fewer in the big radius, count as kill
                self.kills += 1
                kill_reward = 10000
                # print(f"KILLED ENEMY! Total kills: {self.kills}, reward: {kill_reward}")


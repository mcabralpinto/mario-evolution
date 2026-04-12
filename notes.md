# GRAMMAR

- pass (added initially)
    - penalize pass amount of times it appears in the code?
    - just remove "pass"es (to explore search space more effetively). needed to make some changes to coode

- auxiliary perceptions (hole/obstacle/enemy ahead)

- simpler versions of past perceptions (28/3)
    - tweaked (29 - 31/3)
    - added drop and enemy above detection (31/3)
    - readujsted to those requested in project statement (22)

# FITNESS

- stuck (27/3)
    - stuck penalty (not good enough)
    - stuck penalty proportional to stuck time - now he's jumping!

- always jumping (28/3) 
    - discount air time - too punitive! marios don't learn to jump.
    - curriculum (good results. passes 2 levels)
    - curriculum adjustments! (50% -> 10% -> 20%)
    - revert to old and try to get values right (11/4) (10 -> 50)

- penalize closeness to enemies

- bloat control (1/4)
    - reduce (7/4)
    - change to the library version with 2 tournaments (10/4)

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
    - dynamin difficulty window (6/4)
        - possible refinement: heavier weighting of harder levels in the window
        - other: give more time to harder windows

    - mencionar tentar a rotação de seeds com mais seeds mas isso aumentar muito o tempo de treino para gains superficiais



# TRY

- coin reward

- different max tree heights
    - mutation subtree!

- penalize high speeds
    - make a reward that is constant every time he moves forward (don't encourage high velocity)

- try more episodes / difficulties (high seed amount w/ break)

- apply random waits at the start to make enemy timing less predictable, thus forcing better generalization

- more forgiving (? esqueci-me do que isto era)

- try w/ different episode/seed combinations

- ir dando sample de novas seeds de N em N gens~

- evolutionary strategies

- checkpoints
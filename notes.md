# GRAMMAR

- pass (added initially)
    - penalize pass amount of times it appears in the code?
    - just remove "pass"es (to explore search space more effetively). needed to make some changes to coode

- auxiliary perceptions (hole/obstacle/enemy ahead)

- simpler versions of past perceptions (28/3)

# FITNESS

- stuck (27/3)
    - stuck penalty (not good enough)
    - stuck penalty proportional to stuck time - now he's jumping!

- always jumping (28/3) 
    - discount air time - too punitive! marios don't learn to jump.
    - curriculum (good results. passes 2 levels)

# MISC

- added to observation/fit function
    - distance! (initially)
    - current generation (for scheduling)

- mencionar chatice do jump (é preciso tirar e voltar a por!)

- increase episodes! (28/3)

- remove break (29/3) 

# TRY

- coin reward

- different max tree heights

- mutation / crossover probabilities

- bloat control

- no elitism
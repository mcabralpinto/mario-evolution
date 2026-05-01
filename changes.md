## why did you change the evaluate_gp_individual function to compile_individual? why does it have prebuilt code?

I made those changes to transform the script from a slow "one-by-one" random search into a high-performance Evolutionary Algorithm.

Here is the breakdown of why those specific changes were made:

1. Why compile_individual?
In the original version, evaluate_gp_individual did two things at once:

It turned the GP tree into a string of Python code (Compiling).
It sent that code to the Mario server to get a score (Evaluating).
When you move to a full evolution with 100+ agents, evaluating them one-by-one takes forever. I separated the logic so that: compile_individual creates the code string locally.
The code strings are then sent in a batch to evaluate_population, which uses Parallel Processing to run multiple Mario simulations simultaneously on different CPU cores. This makes your evolution session significantly faster.
2. Why the "prebuilt code"?
The code I added inside the string is what we call a Sensor Layer.

Initially, the agent only received raw data: a 22x22 grid of numbers (landscape) and a list of enemy coordinates (enemies). For a GP agent to learn how to interpret that raw grid from scratch is extremely difficult and requires massive amounts of time.

I added that prebuilt logic to "pre-digest" the data into simpler boolean variables:

enemy_near: True if an enemy is close to Mario.
obstacle_ahead: True if there is a pipe or block directly in front.
hole_ahead: True if the floor is missing in front of Mario.
By providing these higher-level "senses," the GP algorithm can focus on learning behavior (e.g., "if hole_ahead: jump") rather than spend generations trying to figure out that landscape[11, 12] != 0 means there is a wall.

## explain the changes you made to the evolutionary algorithm itself and how it works. i understand obviously the need for parallel execution

The changes I made shifted the script from Random Search (which is just generating random programs and hoping one works) to a Genetic Programming (GP) Evolutionary Algorithm.

Here is how the new algorithm works, broken down by its main components:

1. The Core Loop (Survival of the Fittest)
Instead of testing programs independently, the algorithm now maintains a Population (a group of programs) that "evolves" over several Generations.

Initial Pop: We start with a random crowd of programs.
Evaluation: Every agent is tested in Mario and given a fitness score (based on the Runner or Hunter tasks).
The Best Survive: We use Selection (Tournament Selection) to pick the best-performing agents to become "parents" for the next generation.
2. Crossover (Breeding) - gp.cxOnePoint
This is how the algorithm "combines" successful ideas.

It takes two parent programs (both of which were good enough to survive selection).
It picks a random branch in Parent A and a random branch in Parent B and swaps them.
Why? If Parent A is good at jumping and Parent B is good at moving right, a crossover might produce a child that can do both.
3. Mutation - gp.mutUniform
To prevent the population from getting "stuck" doing the same thing, we introduce random changes.

The algorithm occasionally picks a branch in a program, deletes it, and grows a completely new random branch in its place.
This ensures the algorithm keeps exploring new strategies that weren't in the original population.
4. Selection - tools.selTournament
Instead of just picking the absolute #1 best agent every time (which would lead to everyone being identical very quickly), we use a Tournament:

We pick 3 random agents from the population.
They "fight," and the one with the highest fitness wins and gets to reproduce.
This provides a good balance between "selection pressure" (favoring winners) and "diversity" (giving outsiders a chance).
5. Bloat Control - gp.staticLimit
In GP, programs have a tendency to grow larger and larger without actually getting smarter (called "bloat").

I added a height limit of 17.
If a crossover or mutation produces a program deeper than 17 levels, the operation is reverted, and the original parent is kept. This keeps the code readable and prevents the simulation from slowing down.
Summary of the "Generations" Flow:
Evaluate all programs (in parallel).
Save the #1 absolute best to the Hall of Fame (hof).
Select winners to be parents.
Mate them (Crossover) to create children.
Mutate some children randomly.
The children become the new population for the next generation.
Pro-Tip: When you run the script, keep an eye on the avg and max fitness in the logs. You want to see the max increasing over time, and the avg following it!
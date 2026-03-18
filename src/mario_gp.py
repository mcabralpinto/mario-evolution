import operator
import random
import numpy as np
import sys
import textwrap
import pickle
import copy
import argparse
import datetime
from pathlib import Path

# USER IMPORTS (Assuming evaluate is provided in your evaluation.py)
from evaluation import evaluate, evaluate_population

# -----------------------------------------------------------------------------
# USER IMPORTS / MOCKS
# -----------------------------------------------------------------------------
try:
    import marioai
    from agents import CodeAgent, Mario, Sprite
except ImportError:
    # Mocks for standalone testing if libraries are missing
    class Mario:
        KEY_LEFT, KEY_RIGHT, KEY_DOWN, KEY_JUMP, KEY_SPEED = 0, 1, 2, 3, 4

    class Sprite:
        KIND_GOOMBA = 80
        KIND_GOOMBA_WINGED = 81
        KIND_RED_KOOPA = 82
        KIND_RED_KOOPA_WINGED = 83
        KIND_GREEN_KOOPA = 84
        KIND_GREEN_KOOPA_WINGED = 85
        KIND_BULLET_BILL = 86
        KIND_SPIKY = 87
        KIND_SPIKY_WINGED = 88

    class CodeAgent:
        pass

    print("Warning: marioai/agents modules not found. Using mocks.")

from deap import base, creator, tools, gp


# -----------------------------------------------------------------------------
# 0. HELPER: Safe Generator
# -----------------------------------------------------------------------------
def safe_gen_grow(pset, min_, max_, type_=None):
    if type_ is None:
        type_ = pset.ret
    expr = []
    stack = [(0, type_)]
    while stack:
        depth, type_ = stack.pop()
        try:
            has_primitives = len(pset.primitives[type_]) > 0
        except KeyError:
            has_primitives = False
        try:
            has_terminals = len(pset.terminals[type_]) > 0
        except KeyError:
            has_terminals = False

        if not has_terminals and not has_primitives:
            raise IndexError(f"Type '{type_.__name__}' has no primitives/terminals!")

        should_grow = False
        if not has_terminals:
            should_grow = True
        elif not has_primitives:
            should_grow = False
        else:
            if depth < min_:
                should_grow = True
            elif depth >= max_:
                should_grow = False
            else:
                should_grow = random.random() < 0.5

        if should_grow:
            prim = random.choice(pset.primitives[type_])
            expr.append(prim)
            for arg in reversed(prim.args):
                stack.append((depth + 1, arg))
        else:
            term = random.choice(pset.terminals[type_])
            if isinstance(term, type):
                term = term()
            expr.append(term)
    return expr


def indent(text):
    return "\n".join("    " + line for line in text.split("\n"))

BASE_FUNCTION = f"""def corre(action, landscape, enemies, can_jump, on_ground, Mario, Sprite, **kwargs):
    # Process sensors (Heuristics)
    enemy_near = any(abs(ex) < 30 and abs(ey) < 30 for ex, ey, ek in enemies)
    obstacle_ahead = False
    if landscape is not None:
        # Check a few cells in front of Mario (11,11)
        obstacle_ahead = (landscape[11, 12] != 0 or landscape[11, 13] != 0 or landscape[10, 12] != 0)

    hole_ahead = False
    if landscape is not None:
        # Check for floor gap
        hole_ahead = True
        for i in range(12, 16):
            if landscape[i, 12] != 0:
                hole_ahead = False
                break

    # INDIVIDUAL GENERATED CODE vvv
"""


# -----------------------------------------------------------------------------
# 1. TYPE DEFINITIONS (Stripped Down)
# -----------------------------------------------------------------------------
class Expr:
    pass


class Condition:
    pass


class Key:
    pass


class Bool:
    pass


# -----------------------------------------------------------------------------
# 2. PRIMITIVES: STRING BUILDERS
# -----------------------------------------------------------------------------
def str_if_then(cond, expr):
    return f"if {cond}:\n{indent(expr)}"


def str_sequence(expr1, expr2):
    return f"{expr1}\n{expr2}"


def str_set_action(key, val):
    return f"action[{key}] = int({val})"


def str_and(cond1, cond2):
    return f"({cond1} and {cond2})"


def str_or(cond1, cond2):
    return f"({cond1} or {cond2})"


def str_not(cond):
    return f"(not {cond})"


# -----------------------------------------------------------------------------
# 3. GRAMMAR CONFIGURATION
# -----------------------------------------------------------------------------
pset = gp.PrimitiveSetTyped("MAIN", [], Expr)

# Core Logic
pset.addPrimitive(str_if_then, [Condition, Expr], Expr)
pset.addPrimitive(str_sequence, [Expr, Expr], Expr)
pset.addPrimitive(str_set_action, [Key, Bool], Expr)
set.addTerminal("pass", Expr, name="NoOp")

# Boolean Logic
pset.addPrimitive(str_and, [Condition, Condition], Condition, name="AND")
pset.addPrimitive(str_or, [Condition, Condition], Condition, name="OR")
pset.addPrimitive(str_not, [Condition], Condition, name="NOT")

# Senses (Mapped to variables in corre function)
pset.addTerminal("on_ground", Condition, name="IsMarioOnGround")
pset.addTerminal("can_jump", Condition, name="MayMarioJump")
pset.addTerminal("enemy_near", Condition, name="EnemyNear")
pset.addTerminal("obstacle_ahead", Condition, name="ObstacleAhead")
pset.addTerminal("hole_ahead", Condition, name="HoleAhead")

# Constants
pset.addTerminal("True", Bool)
pset.addTerminal("False", Bool)

# Actions
pset.addTerminal("Mario.KEY_RIGHT", Key, name="RIGHT")
pset.addTerminal("Mario.KEY_LEFT", Key, name="LEFT")
pset.addTerminal("Mario.KEY_JUMP", Key, name="JUMP")
pset.addTerminal("Mario.KEY_SPEED", Key, name="SPEED")
pset.addTerminal("Mario.KEY_DOWN", Key, name="DOWN")

# -----------------------------------------------------------------------------
# 4. RANDOM GENERATION SETUP
# -----------------------------------------------------------------------------
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("expr", safe_gen_grow, pset=pset, min_=3, max_=6)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)

def compile_individual(individual):
    """Converts a tree individual into Python code string."""
    code_body = toolbox.compile(individual)
    full_code_str = f"""
{BASE_FUNCTION}
{indent(code_body)}
"""
    return full_code_str


# -----------------------------------------------------------------------------
# 5. PERSISTENCE HELPERS
# -----------------------------------------------------------------------------
def best_individual_code(best_ind, toolbox):
    """Returns the best individual's code as a string."""
    return f"""
{BASE_FUNCTION}
{indent(toolbox.compile(best_ind))}
"""

def save_best_individual(best_ind, toolbox, filename_py=f"mario_best_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py"):
    """Saves the best individual as a readable Python script."""
    if best_ind is None:
        print("No individual to save.")
        return

    fitness_val = best_ind.fitness.values[0] if best_ind.fitness.valid else "Unknown"

    full_code = f"""
# Evolved Mario Controller
# Fitness: {fitness_val}

{best_individual_code(best_ind, toolbox)}
"""
    Path("data/gp_best_agents").mkdir(parents=True, exist_ok=True)
    output_path = Path("data/gp_best_agents") / filename_py
    with output_path.open("w") as f:
        f.write(full_code)
    print(f"Saved executable code to '{filename_py}'")


# -----------------------------------------------------------------------------
# 6. MAIN EXECUTION
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--gen", type=int, default=10)
    parser.add_argument("--pop", type=int, default=20)
    parser.add_argument("--max_height", type=int, default=17)
    args = parser.parse_args()

    random.seed(args.seed)
    
    # Genetic Operators - experiment with these values! try elitism
    toolbox.register("select", tools.selTournament, tournsize=5)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", safe_gen_grow, pset=pset, min_=0, max_=2) 
    toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

    # Decorators to limit tree height
    toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=args.max_height)) 
    toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=args.max_height))

    # Population Initialization
    pop = toolbox.population(n=args.pop)
    hof = tools.HallOfFame(1)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    # Evolutionary Algorithm
    NGEN = args.gen
    CXPB, MUTPB = 0.5, 0.2

    print(f"Starting Evolution: {NGEN} generations, Population size {args.pop}")

    for gen in range(NGEN):
        print(f"\n--- Generation {gen} ---")
        
        # Parallel evaluation
        compiled_pop = [compile_individual(ind) for ind in pop]
        fitnesses = evaluate_population(CodeAgent, compiled_pop)
        
        for ind, fit in zip(pop, fitnesses):
            # Parsimony Pressure: Penalize large trees to fight bloat
            fit -= len(ind) * 0.1 # Adjust this weight based on performance
            ind.fitness.values = (fit,)
        
        hof.update(pop)
        record = stats.compile(pop)
        print(f"Stats:")
        for key, value in record.items():
            print(f"  {key}: {value}")

        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Replace population
        pop[:] = offspring

        # Elitism: Ensure the best individual survives
        if len(hof) > 0:
            pop[0] = toolbox.clone(hof[0])

        print(f"Best fitness in Generation {gen}: {hof[0].fitness.values[0] if hof[0].fitness.valid else 'N/A'}")
        print(f"Best Ind. Height: {hof[0].height}, Size: {len(hof[0])}")
        print("Best Code Structure:")
        print(best_individual_code(hof[0], toolbox))

        # #print another random code from this gen
        # print("Random Code Structure:")
        # print(best_individual_code(random.choice(pop), toolbox))
        

    # Final result
    best_ind = hof[0]
    print(f"\nBest Fitness Found: {best_ind.fitness.values[0]}")
    save_best_individual(best_ind, toolbox, filename_py="gp_mario_best.py")

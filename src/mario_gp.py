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

from src.evaluation import evaluate, evaluate_population
import src.marioai as marioai
from src.agents import CodeAgent, Mario, Sprite
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

BASE_FUNCTION = """def corre(action, landscape, enemies, can_jump, on_ground, Mario, Sprite, **kwargs):
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


class Offset:
    pass


class EnemyKind:
    pass


class TileValue:
    pass


# -----------------------------------------------------------------------------
# 2. PRIMITIVES: STRING BUILDERS
# -----------------------------------------------------------------------------
def str_if_then(cond, expr):
    return f"if {cond}:\n{indent(expr)}"


def str_sequence(expr1, expr2):
    return f"{expr1}\n{expr2}"

def str_action_press(key):
    return f"action[{key}] = 1"

def str_and(cond1, cond2):
    return f"({cond1} and {cond2})"


def str_or(cond1, cond2):
    return f"({cond1} or {cond2})"


def str_not(cond):
    return f"(not {cond})"

def str_check_enemy(posx, posy, comp, enemy_type):
    ''' 
        The goal is to make Mario enemy-aware.
        Currently, posx and posy can be seen as the 
        radius around Mario to check for enemies.
        Comp is a comparator like <, >, == to compare the count of enemies in that radius to a threshold.
        Enemy_type can be used to specify different types of enemies 
    '''
    # Enemies arrive as (x, y, kind) tuples relative to Mario.
    # Keep this a pure boolean expression because it is embedded inside if/and/or trees.
    return (
        f"any((ek == {enemy_type}) and "
        f"(abs(ex) <= {max(1, abs(posx)) * 16}) and "
        f"(abs(ey) <= {max(1, abs(posy)) * 16}) "
        f"for ex, ey, ek in enemies)"
    )

def str_check_obstacle(pos_x, pos_y, comp, obstacle_value):
    """
    Same as above but for obstacles in the landscape.
    """
    x = 11 + pos_x
    y = 11 + pos_y
    # Guard against missing observations and invalid indexes.
    return (
        f"(landscape is not None and 0 <= {y} < landscape.shape[0] and "
        f"0 <= {x} < landscape.shape[1] and landscape[{y}, {x}] {comp} {obstacle_value})"
    )

def str_distance_to_enemy(enemy_type):
    """
    Heuristic to compute distance to the nearest enemy of a given type.
    enemy_type: Integer enemy type.
    """
    return (
        f"any((ek == {enemy_type}) and (abs(ex) <= 32) and (abs(ey) <= 32) "
        f"for ex, ey, ek in enemies)"
    )

def str_gap_ahead():
    return "(landscape is not None and landscape.shape[0] > 11 and landscape.shape[1] > 12 and landscape[11, 12] == 0)"

def str_combine_actions(action1, action2):
    return f"[{action1} or {action2} for {action1}, {action2} in zip({action1}, {action2})]"

# -----------------------------------------------------------------------------
# 3. GRAMMAR CONFIGURATION
# -----------------------------------------------------------------------------
pset = gp.PrimitiveSetTyped("MAIN", [], Expr)
pset.addTerminal("pass", Expr, name="Pass")
# Core Logic
pset.addPrimitive(str_if_then, [Condition, Expr], Expr)
pset.addPrimitive(str_sequence, [Expr, Expr], Expr)
pset.addPrimitive(str_action_press, [Key], Expr)
# pset.addPrimitive(str_combine_actions, [Expr, Expr], Expr, name="CombineActions")

# Boolean Logic
pset.addPrimitive(str_and, [Condition, Condition], Condition, name="AND")
pset.addPrimitive(str_or, [Condition, Condition], Condition, name="OR")
pset.addPrimitive(str_not, [Condition], Condition, name="NOT")
pset.addPrimitive(str_check_enemy, [Offset, Offset, str, EnemyKind], Condition, name="CheckEnemy")
pset.addPrimitive(str_check_obstacle, [Offset, Offset, str, TileValue], Condition, name="CheckObstacle")
pset.addPrimitive(str_distance_to_enemy, [EnemyKind], Condition, name="DistanceToEnemy")
pset.addPrimitive(str_gap_ahead, [], Condition, name="GapAhead")

# Senses (Mapped to variables in corre function)
pset.addTerminal("on_ground", Condition, name="IsMarioOnGround")
pset.addTerminal("can_jump", Condition, name="MayMarioJump")
# Position Terminals (relative to Mario at [11,11])
position_values = [-3, 0, 3]


def int_terminal_name(prefix, value):
    # DEAP terminal names are used as Python identifiers in compiled expressions.
    # Negative values like -1 must not produce names such as X_-1.
    if value < 0:
        return f"{prefix}_NEG{abs(value)}"
    return f"{prefix}_{value}"


for x in position_values:
    pset.addTerminal(x, Offset, name=int_terminal_name("X", x))

for y in position_values:
    pset.addTerminal(y, Offset, name=int_terminal_name("Y", y))

# Or if you want them combined:
for val in position_values:
    pset.addTerminal(val, Offset, name=int_terminal_name("POS", val))

# Comparator Terminals
pset.addTerminal("==", str, name="EQ")
pset.addTerminal("!=", str, name="NE")
pset.addTerminal("<", str, name="LT")
pset.addTerminal(">", str, name="GT")

# Enemy Type Terminals (from Table 1)
enemy_types = {
    2: "GOOMBA",
    3: "GOOMBA_WINGED", 
    4: "RED_KOOPA",
    5: "RED_KOOPA_WINGED",
    6: "GREEN_KOOPA",
    7: "GREEN_KOOPA_WINGED",
    8: "BULLET_BILL",
    9: "SPIKY",
    10: "SPIKY_WINGED",
    12: "PIRANHA_FLOWER",
    13: "SHELL"
}

for value, name in enemy_types.items():
    pset.addTerminal(value, EnemyKind, name=name)

# Obstacle Value Terminals
obstacle_values = {
    -11: "SOFT_OBSTACLE",
    -10: "HARD_OBSTACLE",
    0: "EMPTY_SPACE",
    16: "BRICK",
    20: "ENEMY_OBSTACLE",
    21: "QUESTION_BRICK"
}

for value, name in obstacle_values.items():
    pset.addTerminal(value, TileValue, name=name)

# Boolean Terminals
pset.addTerminal(True, Bool, name="TRUE")
pset.addTerminal(False, Bool, name="FALSE")

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
toolbox.register("expr", safe_gen_grow, pset=pset, min_=3, max_=10)
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
    parser.add_argument(
        "--mode",
        choices=["evolution", "random"],
        default="evolution",
        help="Search mode for GP.",
    )
    args = parser.parse_args()

    random.seed(args.seed)
    
    # Genetic Operators - experiment with these values! try elitism
    toolbox.register("select", tools.selTournament, tournsize=5)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", safe_gen_grow, pset=pset, min_=2, max_=5) 
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
    CXPB, MUTPB = 0.5, 0.35

    if args.mode == "random":
        print(f"Starting Random Search: {NGEN} generations, Population size {args.pop}")

        for gen in range(NGEN):
            print(f"\n--- Generation {gen} ---")
            
            # Parallel evaluation
            compiled_pop = [compile_individual(ind) for ind in pop]
            fitnesses = evaluate_population(CodeAgent, compiled_pop)
            
            for ind, fit in zip(pop, fitnesses):
                # Parsimony Pressure: Penalize large trees to fight bloat
                fit -= len(ind) * 0.01 # Adjust this weight based on performance
                ind.fitness.values = (fit,)
            
            hof.update(pop)
            record = stats.compile(pop)
            print(f"Stats:")
            for key, value in record.items():
                print(f"  {key}: {value}")

                for ind, fit in zip(pop, fitnesses):
                    ind.fitness.values = (fit,)

                hof.update(pop)
                record = stats.compile(pop)
                print(f"Stats: {record}")
    else:
        print(f"Starting Evolution: {NGEN} generations, Population size {args.pop}")

        for gen in range(NGEN):
            print(f"\n--- Generation {gen} ---")
            
            # Parallel evaluation
            compiled_pop = [compile_individual(ind) for ind in pop]
            fitnesses = evaluate_population(CodeAgent, compiled_pop)
            
            for ind, fit in zip(pop, fitnesses):
                # Parsimony Pressure: Penalize large trees to fight bloat
                fit -= len(ind) * 0.01 # Adjust this weight based on performance
                ind.fitness.values = (fit,)
            
            hof.update(pop)
            record = stats.compile(pop)
            print(f"Stats: {record}")

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

            if len(hof) > 0:
                offspring[0] = toolbox.clone(hof[0])

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

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
from typing import Any, cast

from src.evaluation import evaluate, evaluate_population, close_evaluation_pool, set_total_generations
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
            available_primitives = pset.primitives[type_]
            # If we're at/over max depth, prefer a primitive that does not recurse
            # on the same return type (e.g., END(Stmt) over SEQ(Stmt, Program)).
            if depth >= max_:
                non_recursive = [p for p in available_primitives if type_ not in p.args]
                if non_recursive:
                    available_primitives = non_recursive

            prim = random.choice(available_primitives)
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

BASE_FUNCTION = """def corre(action, landscape, enemies, can_jump, on_ground, mario_pos, Mario, Sprite, **kwargs):
"""


# -----------------------------------------------------------------------------
# 1. TYPE DEFINITIONS (Stripped Down)
# -----------------------------------------------------------------------------
class Program:
    pass

class Stmt:
    pass

class Expr:
    pass

class Cond:
    pass

class Comparator:
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


def prog_seq(stmt, program_tail):
    stmt = stmt.rstrip()
    program_tail = program_tail.rstrip()
    if not program_tail:
        return stmt
    return f"{stmt}\n{program_tail}"


def prog_end(stmt):
    return stmt.rstrip()


def stmt_if_else(cond, stmt_true, stmt_false):
    return f"if {cond}:\n{indent(stmt_true)}\nelse:\n{indent(stmt_false)}"


def stmt_if(cond, stmt_true):
    return f"if {cond}:\n{indent(stmt_true)}"


def stmt_action_assign(key, value):
    return f"action[{key}] = {value}"


def cond_and(cond1, cond2):
    return f"({cond1} and {cond2})"


def cond_or(cond1, cond2):
    return f"({cond1} or {cond2})"


def cond_not(cond):
    return f"(not {cond})"


# def cond_check_enemy_ahead(comp, enemy_type):
#     # if there's an enemy in a 3x3 area ahead of Mario (including diagonals)
#     mario_x, mario_y = 11, 11
#     return f"enemies and any((ek {comp} {enemy_type}) and (abs(ex - {mario_x}) <= 3) and (abs(ey - {mario_y}) <= 3) for ex, ey, ek in enemies)"

# def cond_check_obstacle(posx, posy, comp, obstacle_value):
#     x = 11 + posx
#     y = 11 + posy
#     return (
#         f"(landscape is not None and "
#         f"0 <= {y} < landscape.shape[0] and "
#         f"0 <= {x} < landscape.shape[1] and "
#         f"landscape[{y}, {x}] {comp} {obstacle_value})"
#     )


# def cond_gap_ahead(blocks_ahead):
#     mario_x, mario_y = 11, 11
#     target_x = mario_x + blocks_ahead

#     # Expression-only check so GP can inline it into conditions safely.
#     return (
#         "(landscape is not None and "
#         f"0 <= {target_x} < landscape.shape[1] and "
#         f"all(landscape[y, {target_x}] == 0 for y in range({mario_y}, landscape.shape[0])))"
#     )

def cond_check_any_enemy():
    return "(enemies and any((int(ek) in list(range(2, 14))) and ((-16 <= mario_pos[1] - ey <= 32) and (-32 <= ex - mario_pos[0] <= 48)) for ek, ex, ey in enemies))"


def cond_hole():
    return ("(all(landscape[y, 12] == 0 for y in range(12, 22)) or "
           "all(landscape[y, 13] == 0 for y in range(12, 22)))")

def cond_wall():
    return ("(any(landscape[x, y] in [-10, 16, 20, 21] for y in range(11, 14) for x in range(9, 12)))")

# -----------------------------------------------------------------------------
# 3. GRAMMAR CONFIGURATION
# -----------------------------------------------------------------------------
pset = gp.PrimitiveSetTyped("MAIN", [], Program)

# Program structure
pset.addPrimitive(prog_end, [Stmt], Program, name="END")
pset.addPrimitive(prog_seq, [Stmt, Program], Program, name="SEQ")

# Statements
pset.addPrimitive(stmt_if, [Cond, Stmt], Stmt, name="IF")
pset.addPrimitive(stmt_if_else, [Cond, Stmt, Stmt], Stmt, name="IF_ELSE")
pset.addPrimitive(stmt_action_assign, [Key, Bool], Stmt, name="SET_ACTION")

# Boolean logic
pset.addPrimitive(cond_and, [Cond, Cond], Cond, name="AND")
pset.addPrimitive(cond_or, [Cond, Cond], Cond, name="OR")
pset.addPrimitive(cond_not, [Cond], Cond, name="NOT")
# pset.addPrimitive(cond_check_enemy_ahead, [Comparator, EnemyKind], Cond, name="CheckEnemy")
# pset.addPrimitive(cond_check_obstacle, [Offset, Offset, Comparator, TileValue], Cond, name="CheckObstacle")
# pset.addPrimitive(cond_gap_ahead, [Offset], Cond, name="GapAhead")
pset.addPrimitive(cond_check_any_enemy, [], Cond, name="CheckAnyEnemy")
pset.addPrimitive(cond_hole, [], Cond, name="HoleAhead")
pset.addPrimitive(cond_wall, [], Cond, name="WallAhead")

# Senses
pset.addTerminal("on_ground", Cond, name="IsMarioOnGround")
pset.addTerminal("can_jump", Cond, name="MayMarioJump")

# Position terminals
position_values = [-3, -2, -1, 0, 1, 2, 3]


def int_terminal_name(prefix, value):
    if value < 0:
        return f"{prefix}_NEG{abs(value)}"
    return f"{prefix}_{value}"


for x in position_values:
    pset.addTerminal(x, Offset, name=int_terminal_name("X", x))

for y in position_values:
    pset.addTerminal(y, Offset, name=int_terminal_name("Y", y))

# Comparators
pset.addTerminal("==", Comparator, name="EQ")
pset.addTerminal("!=", Comparator, name="NE")
pset.addTerminal("<", Comparator, name="LT")
pset.addTerminal(">", Comparator, name="GT")

# Enemy types
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
    13: "SHELL",
}

for value, name in enemy_types.items():
    pset.addTerminal(value, EnemyKind, name=name)

# Obstacle values
obstacle_values = {
    -11: "SOFT_OBSTACLE",
    -10: "HARD_OBSTACLE",
    16: "BRICK",
    20: "ENEMY_OBSTACLE",
}

for value, name in obstacle_values.items():
    pset.addTerminal(value, TileValue, name=name)

# Numeric literals for action assignments
pset.addTerminal(True, Bool, name="1")
pset.addTerminal(False, Bool, name="0")

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
FitnessMax = cast(type[base.Fitness], creator.FitnessMax)
Individual = cast(type[gp.PrimitiveTree], creator.Individual)

toolbox: Any = base.Toolbox()
toolbox.register("expr", safe_gen_grow, pset=pset, min_=3, max_=10)
toolbox.register("individual", tools.initIterate, Individual, toolbox.expr)
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


def evaluate_invalid_individuals(population, generation):
    """Evaluate only individuals with invalid fitness and update them in-place."""
    invalid_entries = [(idx, ind) for idx, ind in enumerate(population) if not ind.fitness.valid]
    if not invalid_entries:
        return

    invalid_indices = [idx for idx, _ in invalid_entries]
    compiled_invalid = [compile_individual(ind) for _, ind in invalid_entries]
    fitnesses = evaluate_population(CodeAgent, compiled_invalid, generation=generation)

    for idx, fit in zip(invalid_indices, fitnesses):
        population[idx].fitness.values = (fit,)


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
    parser.add_argument("--max_height", type=int, default=14)
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
    set_total_generations(NGEN)
    CXPB, MUTPB = 0.5, 0.5
    ELITISM = True

    if args.mode == "random":
        print(f"Starting Random Search: {NGEN} generations, Population size {args.pop}")

        for gen in range(NGEN):
            print(f"\n--- Generation {gen} ---")
            
            # Parallel evaluation
            compiled_pop = [compile_individual(ind) for ind in pop]
            fitnesses = evaluate_population(CodeAgent, compiled_pop, generation=gen)
            
            for ind, fit in zip(pop, fitnesses):
                # Parsimony Pressure: Penalize large trees to fight bloat
                # fit -= len(ind) * 0.01 # Adjust this weight based on performance
                ind.fitness.values = (fit,)
            
            hof.update(pop)
            record = stats.compile(pop)
            print(f"\033[91mMax:\033[0m {record['max']:.3f}, \033[94mMin:\033[0m {record['min']:.3f}, \033[92mAvg:\033[0m {record['avg']:.3f}, \033[93mStd:\033[0m {record['std']:.3f}")

    else:
        print(f"Starting Evolution: {NGEN} generations, Population size {args.pop}")

        try:
            for gen in range(NGEN):
                print(f"\n--- Generation {gen} ---")

                # Parallel evaluation (only individuals modified by variation)
                evaluate_invalid_individuals(pop, generation=gen)

                hof.update(pop)
                record = stats.compile(pop)
                print(f"\033[91mMax:\033[0m {record['max']:.3f}, \033[94mMin:\033[0m {record['min']:.3f}, \033[92mAvg:\033[0m {record['avg']:.3f}, \033[93mStd:\033[0m {record['std']:.3f}")

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

                if len(hof) > 0 and ELITISM:
                    offspring[0] = toolbox.clone(hof[0])

                # Replace population
                pop[:] = offspring
        finally:
            close_evaluation_pool()

        print(f"Best fitness in Generation {NGEN}: {hof[0].fitness.values[0] if hof[0].fitness.valid else 'N/A'}")
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

# .\env\Scripts\python.exe -m src.mario_gp --pop 100 --gen 50
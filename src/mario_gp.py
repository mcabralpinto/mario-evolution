import operator
import random
import numpy as np
import sys
import textwrap
import pickle
import copy
import argparse
import datetime
import re
from typing import Any, Callable, cast
from pathlib import Path

from src.evaluation import evaluate, evaluate_population
import src.marioai as marioai
from src.agents import CodeAgent, Mario, Sprite
from deap import base, creator, tools, gp

MAX_LOOP_STEPS = 64
PARSIMONY_COEFF = 0.02


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


def coerce_fitness(value):
    if value is None:
        return 0.0
    return float(value)


def action_diversity_bonus(code_str):
    keys = set(re.findall(r"action\[Mario\.(KEY_[A-Z]+)\]\s*=\s*int\(True\)", code_str))
    if not keys:
        return -10.0

    bonus = 12.0 * len(keys)
    if keys == {"KEY_RIGHT"}:
        bonus -= 60.0
    if "KEY_JUMP" in keys:
        bonus += 20.0
    if "KEY_SPEED" in keys:
        bonus += 8.0
    return bonus

BASE_FUNCTION = f"""def corre(action, landscape, enemies, can_jump, on_ground, Mario, Sprite, **kwargs):
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
        wall_ahead = any(landscape[row, 12] in wall_tiles for row in range(9, 12)) or \
                     any(landscape[row, 13] in wall_tiles for row in range(9, 12))
        
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

def while_loop(cond, expr):
    return (
        f"for _ in range({MAX_LOOP_STEPS}):\n"
        f"    if not ({cond}):\n"
        "        break\n"
        f"{indent(expr)}"
    )


# -----------------------------------------------------------------------------
# 3. GRAMMAR CONFIGURATION
# -----------------------------------------------------------------------------
pset = gp.PrimitiveSetTyped("MAIN", [], Expr)

# Core Logic
pset.addPrimitive(str_if_then, [Condition, Expr], Expr)
pset.addPrimitive(str_sequence, [Expr, Expr], Expr)
pset.addPrimitive(str_set_action, [Key, Bool], Expr)
pset.addPrimitive(while_loop, [Condition, Expr], Expr, name="WHILE")
pset.addTerminal("pass", Expr, name="NoOp")

# Boolean Logic
pset.addPrimitive(str_and, [Condition, Condition], Condition, name="AND")
pset.addPrimitive(str_or, [Condition, Condition], Condition, name="OR")
pset.addPrimitive(str_not, [Condition], Condition, name="NOT")

# Senses (Mapped to variables in corre function)
pset.addTerminal("on_ground", Condition, name="IsMarioOnGround")
pset.addTerminal("can_jump", Condition, name="MayMarioJump")
pset.addTerminal("enemy_near", Condition, name="EnemyNear")
pset.addTerminal("wall_ahead", Condition, name="WallAhead")
pset.addTerminal("obstacle_ahead", Condition, name="ObstacleAhead")
pset.addTerminal("hole_ahead", Condition, name="HoleAhead")
pset.addTerminal("enemy_ahead", Condition, name="EnemyAhead")
pset.addTerminal("enemy_above", Condition, name="EnemyAbove")
pset.addTerminal("enemy_behind", Condition, name="EnemyBehind")
pset.addTerminal("slope_ahead", Condition, name="SlopeAhead")
pset.addTerminal("danger_ahead", Condition, name="DangerAhead")

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
toolbox.register("expr", safe_gen_grow, pset=pset, min_=2, max_=9)
expr_fn = cast(Callable[[], Any], getattr(toolbox, "expr"))
toolbox.register("individual", tools.initIterate, creator.Individual, expr_fn)
individual_fn = cast(Callable[[], Any], getattr(toolbox, "individual"))
toolbox.register("population", tools.initRepeat, list, individual_fn)
toolbox.register("compile", gp.compile, pset=pset)
compile_fn = cast(Callable[[Any], str], getattr(toolbox, "compile"))

def compile_individual(individual):
    """Converts a tree individual into Python code string."""
    code_body = compile_fn(individual)
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
{indent(compile_fn(best_ind))}
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
    parser.add_argument("--max_height", type=int, default=28)
    parser.add_argument("--max_loop_steps", type=int, default=64)
    parser.add_argument(
        "--mode",
        choices=["evolution", "random"],
        default="evolution",
        help="Search mode for GP.",
    )
    args = parser.parse_args()
    MAX_LOOP_STEPS = max(1, args.max_loop_steps)

    random.seed(args.seed)
    
    # Genetic Operators - experiment with these values! try elitism
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("mate", gp.cxOnePoint)
    toolbox.register("expr_mut", safe_gen_grow, pset=pset, min_=0, max_=4) 
    expr_mut_fn = cast(Callable[[], Any], getattr(toolbox, "expr_mut"))
    toolbox.register("mutate", gp.mutUniform, expr=expr_mut_fn, pset=pset)
    select_fn = cast(Callable[[list, int], list], getattr(toolbox, "select"))
    mate_fn = cast(Callable[[Any, Any], Any], getattr(toolbox, "mate"))
    mutate_fn = cast(Callable[[Any], Any], getattr(toolbox, "mutate"))
    clone_fn = cast(Callable[[Any], Any], getattr(toolbox, "clone"))
    decorate_fn = cast(Callable[[str, Any], Any], getattr(toolbox, "decorate"))
    population_fn = cast(Callable[..., list], getattr(toolbox, "population"))

    # Decorators to limit tree height
    decorate_fn("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=args.max_height))
    decorate_fn("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=args.max_height))

    # Population Initialization
    pop = population_fn(n=args.pop)
    hof = tools.HallOfFame(1)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    # Evolutionary Algorithm
    NGEN = args.gen
    CXPB, MUTPB = 0.5, 0.45

    if args.mode == "random":
        print(f"Starting Random Search: {NGEN} generations, Population size {args.pop}")

        for gen in range(NGEN):
            print(f"\n--- Generation {gen} ---")
            pop = population_fn(n=args.pop)
            
            # Parallel evaluation
            compiled_pop = [compile_individual(ind) for ind in pop]
            fitnesses = evaluate_population(CodeAgent, compiled_pop)
            
            for ind, raw_fit, code_str in zip(pop, fitnesses, compiled_pop):
                # Parsimony Pressure: Penalize large trees to fight bloat
                fit = (
                    coerce_fitness(raw_fit)
                    - len(ind) * PARSIMONY_COEFF
                    + action_diversity_bonus(code_str)
                )
                ind.fitness.values = (fit,)
            
            hof.update(pop)
            record = stats.compile(pop)
            print(f"Stats: {record}")
    else:
        print(f"Starting Evolution: {NGEN} generations, Population size {args.pop}")
        
        # Parallel evaluation
        compiled_pop = [compile_individual(ind) for ind in pop]
        fitnesses = evaluate_population(CodeAgent, compiled_pop)
        
        for ind, raw_fit, code_str in zip(pop, fitnesses, compiled_pop):
            # Parsimony Pressure: Penalize large trees to fight bloat
            fit = (
                coerce_fitness(raw_fit)
                - len(ind) * PARSIMONY_COEFF
                + action_diversity_bonus(code_str)
            )
            ind.fitness.values = (fit,)
        
        hof.update(pop)

        for gen in range(NGEN):
            print(f"\n--- Generation {gen} ---")
            record = stats.compile(pop)
            print(f"Stats: {record}")

            # Select the next generation individuals
            offspring = select_fn(pop, len(pop))
            offspring = list(map(clone_fn, offspring))

            # Apply crossover and mutation
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < CXPB:
                    mate_fn(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            for mutant in offspring:
                if random.random() < MUTPB:
                    mutate_fn(mutant)
                    del mutant.fitness.values
            
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            compiled_invalid = [compile_individual(ind) for ind in invalid_ind]
            fitnesses = evaluate_population(CodeAgent, compiled_invalid)
            
            for ind, raw_fit, code_str in zip(invalid_ind, fitnesses, compiled_invalid):
                ind.fitness.values = (
                    coerce_fitness(raw_fit)
                    - len(ind) * PARSIMONY_COEFF
                    + action_diversity_bonus(code_str),
                )
            pop[:] = offspring

            if len(hof) > 0:
                worst_idx = min(range(len(pop)), key=lambda i: pop[i].fitness.values[0])
                pop[worst_idx] = clone_fn(hof[0])
            hof.update(pop)
            record = stats.compile(pop)
            print(f"Stats: {record}")
        print(f"Best fitness in Generation {gen}: {hof[0].fitness.values[0] if hof[0].fitness.valid else 'N/A'}")
        print(f"Best Ind. Height: {hof[0].height}, Size: {len(hof[0])}")
        print("Best Code Structure:")
        print(best_individual_code(hof[0], toolbox))


    # Final result
    best_ind = hof[0]
    print(f"\nBest Fitness Found: {best_ind.fitness.values[0]}")
    save_best_individual(best_ind, toolbox, filename_py="gp_mario_best.py")

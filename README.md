# Boids Flocking Simulation

This repository contains a 2D flocking simulation in Python using `pygame`. The simulation demonstrates how believable group motion emerges from three local rules applied by each boid:

- **Separation**: avoid crowding neighbors that are too close.
- **Alignment**: steer toward the average heading of nearby neighbors.
- **Cohesion**: steer toward the local center of mass.

## Features

- At least 30 boids on screen by default (`60` spawn initially).
- Continuous position, velocity, and acceleration updates.
- Neighbor detection using configurable neighborhood and separation radii.
- Speed and steering-force limiting for stable motion.
- Screen wrapping to keep boids inside the play space.
- Triangle rendering so each boid points in its direction of travel.
- Optional click-to-seek target for an extension challenge.
- Command-line parameters for tuning boid count and flocking weights.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python boids.py
```

## Useful command-line options

```bash
python boids.py --boids 100 --neighbor-radius 70 --separation-radius 28 \
  --separation-weight 1.8 --alignment-weight 1.0 --cohesion-weight 0.9
```

Additional options:

- `--max-speed`
- `--max-force`
- `--target-weight`
- `--debug` to draw neighborhood circles

## Controls

- **Left click**: create a goal point the flock will gently seek.
- **Right click**: clear the goal point.
- **Close window**: exit the simulation.

## Assignment mapping

### Minimum requirements

- **Boid structure**: `Boid` stores position, velocity, acceleration, and provides `update()`, `draw()`, and `flock()`.
- **Neighbor detection**: every boid checks every other boid inside the neighborhood radius.
- **Flocking rules**: separation, alignment, and cohesion are each implemented as separate methods.
- **Motion constraints**: steering force and velocity are both capped.
- **Boundary handling**: screen wrapping keeps agents in bounds.

### Intermediate requirements

- Boids render as triangles facing their heading.
- Main weights and radii are configurable via CLI arguments.
- Number of boids can be changed with `--boids`.

### Advanced extension included

- Mouse clicks create a target point that the flock seeks.

## Reflection notes

- **Biggest visible effect**: separation usually has the biggest immediate effect because it prevents overlap and creates the spacing that makes the flock readable.
- **If separation is too strong**: the flock breaks apart into jittery individuals that constantly repel each other.
- **If cohesion is too strong**: boids collapse into dense clumps and may spiral or bunch unrealistically.
- **Why this is emergent behavior**: no single boid controls the group, yet coordinated flock motion appears from local interactions.
- **Time complexity**: the straightforward neighbor check is `O(n²)` because each boid compares itself to every other boid.
- **Optimization ideas**: use a uniform grid, quadtree, or spatial hashing so each boid only checks nearby partitions instead of the whole flock.

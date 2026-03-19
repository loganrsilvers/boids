import argparse
import math
import random
from dataclasses import dataclass
from typing import Iterable, Optional

import pygame

WIDTH = 800
HEIGHT = 600
BACKGROUND = (20, 20, 30)
BOID_COLOR = (240, 240, 255)
TARGET_COLOR = (255, 170, 80)


@dataclass
class Vector2:
    x: float = 0.0
    y: float = 0.0

    def add(self, other: "Vector2") -> None:
        self.x += other.x
        self.y += other.y

    def sub(self, other: "Vector2") -> None:
        self.x -= other.x
        self.y -= other.y

    def mult(self, scalar: float) -> None:
        self.x *= scalar
        self.y *= scalar

    def div(self, scalar: float) -> None:
        if scalar != 0:
            self.x /= scalar
            self.y /= scalar

    def mag(self) -> float:
        return math.hypot(self.x, self.y)

    def normalize(self) -> None:
        magnitude = self.mag()
        if magnitude > 0:
            self.div(magnitude)

    def limit(self, max_value: float) -> None:
        magnitude = self.mag()
        if magnitude > max_value:
            self.normalize()
            self.mult(max_value)

    def set_mag(self, magnitude: float) -> None:
        self.normalize()
        self.mult(magnitude)

    def copy(self) -> "Vector2":
        return Vector2(self.x, self.y)


@dataclass
class Config:
    width: int = WIDTH
    height: int = HEIGHT
    num_boids: int = 60
    neighbor_radius: float = 55.0
    separation_radius: float = 24.0
    max_speed: float = 4.0
    max_force: float = 0.08
    separation_weight: float = 1.6
    alignment_weight: float = 1.0
    cohesion_weight: float = 1.0
    target_weight: float = 0.45
    show_debug: bool = False


class Boid:
    def __init__(self, config: Config):
        self.config = config
        self.position = Vector2(
            random.uniform(0, config.width), random.uniform(0, config.height)
        )
        self.velocity = Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
        if self.velocity.mag() == 0:
            self.velocity = Vector2(1, 0)
        self.acceleration = Vector2(0, 0)

    def apply_force(self, force: Vector2) -> None:
        self.acceleration.add(force)

    def flock(self, boids: Iterable["Boid"], target: Optional[Vector2] = None) -> None:
        separation_force = self.separation(boids)
        alignment_force = self.alignment(boids)
        cohesion_force = self.cohesion(boids)

        separation_force.mult(self.config.separation_weight)
        alignment_force.mult(self.config.alignment_weight)
        cohesion_force.mult(self.config.cohesion_weight)

        self.apply_force(separation_force)
        self.apply_force(alignment_force)
        self.apply_force(cohesion_force)

        if target is not None:
            target_force = self.seek(target)
            target_force.mult(self.config.target_weight)
            self.apply_force(target_force)

    def separation(self, boids: Iterable["Boid"]) -> Vector2:
        steer = Vector2(0, 0)
        count = 0

        for other in boids:
            if other is self:
                continue
            distance = get_distance(self.position, other.position)
            if 0 < distance < self.config.separation_radius:
                diff = self.position.copy()
                diff.sub(other.position)
                diff.normalize()
                diff.div(distance)
                steer.add(diff)
                count += 1

        if count > 0:
            steer.div(count)

        if steer.mag() > 0:
            steer.set_mag(self.config.max_speed)
            steer.sub(self.velocity)
            steer.limit(self.config.max_force)

        return steer

    def alignment(self, boids: Iterable["Boid"]) -> Vector2:
        average_velocity = Vector2(0, 0)
        count = 0

        for other in boids:
            if other is self:
                continue
            distance = get_distance(self.position, other.position)
            if distance < self.config.neighbor_radius:
                average_velocity.add(other.velocity)
                count += 1

        if count == 0:
            return Vector2(0, 0)

        average_velocity.div(count)
        average_velocity.set_mag(self.config.max_speed)
        average_velocity.sub(self.velocity)
        average_velocity.limit(self.config.max_force)
        return average_velocity

    def cohesion(self, boids: Iterable["Boid"]) -> Vector2:
        center_of_mass = Vector2(0, 0)
        count = 0

        for other in boids:
            if other is self:
                continue
            distance = get_distance(self.position, other.position)
            if distance < self.config.neighbor_radius:
                center_of_mass.add(other.position)
                count += 1

        if count == 0:
            return Vector2(0, 0)

        center_of_mass.div(count)
        return self.seek(center_of_mass)

    def seek(self, target: Vector2) -> Vector2:
        desired = target.copy()
        desired.sub(self.position)
        if desired.mag() == 0:
            return Vector2(0, 0)
        desired.set_mag(self.config.max_speed)

        steer = desired.copy()
        steer.sub(self.velocity)
        steer.limit(self.config.max_force)
        return steer

    def update(self) -> None:
        self.velocity.add(self.acceleration)
        self.velocity.limit(self.config.max_speed)
        self.position.add(self.velocity)
        self.acceleration = Vector2(0, 0)

        if self.position.x < 0:
            self.position.x = self.config.width
        elif self.position.x > self.config.width:
            self.position.x = 0

        if self.position.y < 0:
            self.position.y = self.config.height
        elif self.position.y > self.config.height:
            self.position.y = 0

    def draw(self, screen: pygame.Surface) -> None:
        angle = math.atan2(self.velocity.y, self.velocity.x)
        size = 8
        front = (
            self.position.x + math.cos(angle) * size,
            self.position.y + math.sin(angle) * size,
        )
        back_left = (
            self.position.x + math.cos(angle + 2.6) * size * 0.8,
            self.position.y + math.sin(angle + 2.6) * size * 0.8,
        )
        back_right = (
            self.position.x + math.cos(angle - 2.6) * size * 0.8,
            self.position.y + math.sin(angle - 2.6) * size * 0.8,
        )
        pygame.draw.polygon(screen, BOID_COLOR, (front, back_left, back_right))

        if self.config.show_debug:
            pygame.draw.circle(
                screen,
                (70, 90, 110),
                (int(self.position.x), int(self.position.y)),
                int(self.config.neighbor_radius),
                1,
            )


def get_distance(a: Vector2, b: Vector2) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="2D flocking simulation with boids.")
    parser.add_argument("--boids", type=int, default=60, help="Number of boids to spawn.")
    parser.add_argument(
        "--neighbor-radius",
        type=float,
        default=55.0,
        help="Radius used for alignment and cohesion.",
    )
    parser.add_argument(
        "--separation-radius",
        type=float,
        default=24.0,
        help="Radius used for close-range avoidance.",
    )
    parser.add_argument("--separation-weight", type=float, default=1.6)
    parser.add_argument("--alignment-weight", type=float, default=1.0)
    parser.add_argument("--cohesion-weight", type=float, default=1.0)
    parser.add_argument("--target-weight", type=float, default=0.45)
    parser.add_argument("--max-speed", type=float, default=4.0)
    parser.add_argument("--max-force", type=float, default=0.08)
    parser.add_argument(
        "--debug", action="store_true", help="Show neighborhood radius guides."
    )
    return parser


def run() -> None:
    args = build_parser().parse_args()
    config = Config(
        num_boids=args.boids,
        neighbor_radius=args.neighbor_radius,
        separation_radius=args.separation_radius,
        max_speed=args.max_speed,
        max_force=args.max_force,
        separation_weight=args.separation_weight,
        alignment_weight=args.alignment_weight,
        cohesion_weight=args.cohesion_weight,
        target_weight=args.target_weight,
        show_debug=args.debug,
    )

    pygame.init()
    screen = pygame.display.set_mode((config.width, config.height))
    pygame.display.set_caption("Boids Flocking Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 18)

    boids = [Boid(config) for _ in range(config.num_boids)]
    target: Optional[Vector2] = None
    running = True

    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    target = Vector2(mouse_x, mouse_y)
                elif event.button == 3:
                    target = None

        screen.fill(BACKGROUND)

        for boid in boids:
            boid.flock(boids, target)
            boid.update()
            boid.draw(screen)

        instructions = (
            f"boids={config.num_boids}  left click=set target  right click=clear target"
        )
        text_surface = font.render(instructions, True, (200, 200, 220))
        screen.blit(text_surface, (10, 10))

        if target is not None:
            pygame.draw.circle(
                screen,
                TARGET_COLOR,
                (int(target.x), int(target.y)),
                7,
                width=2,
            )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()

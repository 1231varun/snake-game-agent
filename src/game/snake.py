"""
Snake Game implementation
"""

import random

import numpy as np
import pygame

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Define directions
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3


class SnakeGame:
    """
    Snake game implementation that can be used for both human play
    and agent training through reinforcement learning.
    """

    def __init__(self, width=800, height=600, grid_size=20, max_steps_without_food=100):
        """Initialize the snake game."""
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.grid_width = width // grid_size
        self.grid_height = height // grid_size
        self.max_steps_without_food = max_steps_without_food

        # Initialize pygame if not already initialized
        if not pygame.get_init():
            pygame.init()

        # Surface to draw the game on
        self.screen = pygame.Surface((width, height))

        # Game clock
        self.clock = pygame.time.Clock()

        # Reset the game
        self.reset()

    def reset(self):
        """Reset the game state."""
        # Initial snake position (in grid coordinates)
        self.snake = [(self.grid_width // 2, self.grid_height // 2)]

        # Initial direction
        self.direction = RIGHT

        # Initial score
        self.score = 0

        # Track all empty cells for efficient food placement
        self.update_empty_cells()

        # Generate first food
        self.generate_food()

        # Game over state
        self.game_over = False

        # Steps since last food
        self.steps_since_food = 0

        # Total steps
        self.total_steps = 0

        # Return the initial state (useful for RL)
        return self.get_state()

    def update_empty_cells(self):
        """Update the list of empty cells for efficient food placement."""
        self.empty_cells = set()
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                position = (x, y)
                if position not in self.snake:
                    self.empty_cells.add(position)

    def generate_food(self):
        """Generate food at a random empty location."""
        # Place food in a random empty cell
        if self.empty_cells:
            # If snake is small (length 1-3), place food closer to the snake head
            # to make initial learning easier
            if len(self.snake) <= 3:
                head_x, head_y = self.snake[0]
                close_cells = []

                # Get empty cells within a limited range of the snake head
                range_limit = 5 + len(self.snake) * 2  # Increase range as snake grows
                for cell in self.empty_cells:
                    x, y = cell
                    distance = abs(x - head_x) + abs(y - head_y)
                    if distance <= range_limit:
                        close_cells.append(cell)

                # If we found close cells, choose from them
                if close_cells:
                    self.food = random.choice(close_cells)
                    self.empty_cells.remove(self.food)
                    return

            # Default case: choose from all empty cells
            self.food = random.choice(tuple(self.empty_cells))
            self.empty_cells.remove(self.food)
        else:
            # No empty cells, game won!
            self.food = None
            self.game_over = True

    def get_state(self):
        """
        Get the current state of the game.
        Returns a dictionary with game state information.
        For RL, you might want to convert this to a specific format.
        """
        return {
            "snake": self.snake.copy(),
            "snake_head": self.snake[0],
            "food": self.food,
            "direction": self.direction,
            "score": self.score,
            "game_over": self.game_over,
        }

    def get_state_for_agent(self):
        """
        Get a simplified state representation for the agent.
        Returns a numpy array with:
        - Danger straight, right, left (bool)
        - Direction (one-hot)
        - Food direction (bool)
        """
        head_x, head_y = self.snake[0]

        # Check danger in each direction (collision with wall or self)
        point_u = (head_x, head_y - 1)
        point_r = (head_x + 1, head_y)
        point_d = (head_x, head_y + 1)
        point_l = (head_x - 1, head_y)

        # Current direction
        dir_u = self.direction == UP
        dir_r = self.direction == RIGHT
        dir_d = self.direction == DOWN
        dir_l = self.direction == LEFT

        # Danger straight, right, left relative to current direction
        danger_straight = (
            (dir_u and self._is_collision(point_u))
            or (dir_r and self._is_collision(point_r))
            or (dir_d and self._is_collision(point_d))
            or (dir_l and self._is_collision(point_l))
        )

        danger_right = (
            (dir_u and self._is_collision(point_r))
            or (dir_r and self._is_collision(point_d))
            or (dir_d and self._is_collision(point_l))
            or (dir_l and self._is_collision(point_u))
        )

        danger_left = (
            (dir_u and self._is_collision(point_l))
            or (dir_r and self._is_collision(point_u))
            or (dir_d and self._is_collision(point_r))
            or (dir_l and self._is_collision(point_d))
        )

        # Food direction
        food_x, food_y = self.food
        food_left = food_x < head_x
        food_right = food_x > head_x
        food_up = food_y < head_y
        food_down = food_y > head_y

        # Compile state array
        state = np.array(
            [
                # Danger
                danger_straight,
                danger_right,
                danger_left,
                # Direction
                dir_l,
                dir_r,
                dir_u,
                dir_d,
                # Food direction
                food_left,
                food_right,
                food_up,
                food_down,
            ],
            dtype=int,
        )

        return state

    def _is_collision(self, point):
        """Check if a point collides with the snake or walls."""
        x, y = point

        # Check wall collision
        if x < 0 or x >= self.grid_width or y < 0 or y >= self.grid_height:
            return True

        # Check snake collision (except for the tail which will move)
        if point in self.snake[:-1]:
            return True

        return False

    def step(self, action=None):
        """
        Advance the game by one step.
        For human mode, action is None (use self.direction).
        For agent mode, action is 0 (straight), 1 (right), 2 (left).

        Returns: (new_state, reward, done, info)
        """
        if self.game_over:
            return self.get_state(), 0, True, {"score": self.score}

        # Process action for agent
        if action is not None:
            # 0 = straight, 1 = right turn, 2 = left turn
            if action == 1:  # Right turn
                self.direction = (self.direction + 1) % 4
            elif action == 2:  # Left turn
                self.direction = (self.direction - 1) % 4

        # Move the snake
        head_x, head_y = self.snake[0]
        if self.direction == UP:
            new_head = (head_x, head_y - 1)
        elif self.direction == RIGHT:
            new_head = (head_x + 1, head_y)
        elif self.direction == DOWN:
            new_head = (head_x, head_y + 1)
        elif self.direction == LEFT:
            new_head = (head_x - 1, head_y)

        # Check collision
        if self._is_collision(new_head):
            self.game_over = True
            return self.get_state(), -1, True, {"score": self.score}

        # Update empty cells - remove the new head position
        if new_head in self.empty_cells:
            self.empty_cells.remove(new_head)

        # Add new head
        self.snake.insert(0, new_head)

        # Check if food is eaten
        reward = 0
        if self.snake[0] == self.food:
            # Increase score
            self.score += 1
            reward = 1

            # Update empty cells (don't add back the tail)
            self.update_empty_cells()

            # Generate new food
            self.generate_food()

            # Reset steps since food
            self.steps_since_food = 0
        else:
            # Remove tail and add it back to empty cells
            tail = self.snake.pop()
            self.empty_cells.add(tail)

            # Small negative reward for each step without food
            reward = -0.01

            # Increase steps since food
            self.steps_since_food += 1

            # Check if snake is stuck in a loop - more aggressive timeout
            # Use snake length as a factor, but with a lower multiplier
            if self.steps_since_food > self.max_steps_without_food * len(self.snake):
                self.game_over = True
                reward = -1
                return self.get_state(), reward, self.game_over, {"score": self.score, "timeout": True}

            # Add distance-based rewards to guide the snake toward food
            head_x, head_y = self.snake[0]
            food_x, food_y = self.food

            # Calculate Manhattan distance to food
            old_distance = abs(head_x - food_x) + abs(head_y - food_y)

            # Check if we got closer to the food
            if old_distance > 0:
                # Small positive reward for getting closer to food
                # Small negative reward for getting farther from food
                distance_reward = 0.1 / old_distance
                reward += distance_reward

        # Increment total steps
        self.total_steps += 1

        return self.get_state(), reward, self.game_over, {"score": self.score}

    def process_event(self, event):
        """Process pygame events for human control."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and self.direction != DOWN:
                self.direction = UP
            elif event.key == pygame.K_RIGHT and self.direction != LEFT:
                self.direction = RIGHT
            elif event.key == pygame.K_DOWN and self.direction != UP:
                self.direction = DOWN
            elif event.key == pygame.K_LEFT and self.direction != RIGHT:
                self.direction = LEFT

    def render(self):
        """Render the game state to the screen surface."""
        # Clear the screen
        self.screen.fill(BLACK)

        # Draw the snake
        for i, (x, y) in enumerate(self.snake):
            color = GREEN if i == 0 else BLUE  # Head is green, body is blue
            rect = pygame.Rect(x * self.grid_size, y * self.grid_size, self.grid_size, self.grid_size)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 1)  # Border

        # Draw the food
        if self.food:
            rect = pygame.Rect(
                self.food[0] * self.grid_size, self.food[1] * self.grid_size, self.grid_size, self.grid_size
            )
            pygame.draw.rect(self.screen, RED, rect)

        # Draw score
        font = pygame.font.SysFont("Arial", 20)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw game over text
        if self.game_over:
            font = pygame.font.SysFont("Arial", 48)
            game_over_text = font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(game_over_text, text_rect)

            font = pygame.font.SysFont("Arial", 24)
            restart_text = font.render("Press R to restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
            self.screen.blit(restart_text, restart_rect)

        return self.screen

    def tick(self, fps=10):
        """Control the game speed."""
        self.clock.tick(fps)

    def close(self):
        """Close the game."""
        # No need to close anything since we're using a Surface

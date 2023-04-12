import pygame
import random
from enum import Enum
import numpy as np


pygame.init()


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


# RGB colors definition
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)


class SnakeGameAI:

    def __init__(self, snake_speed=200, scr_width=32, scr_height=20, scaling_factor=10):
        # set display
        self.snake_speed = snake_speed
        self.scr_width = scr_width
        self.scr_height = scr_height
        self.dis = pygame.display.set_mode((self.scr_width * scaling_factor,
                                            self.scr_height * scaling_factor))
        self.screen = pygame.Surface((self.scr_width, self.scr_height))
        pygame.display.set_caption('OOP SNAKE game by Ofir')
        self.font_style = pygame.font.SysFont("bahnschrift", 50)
        self.score_font = pygame.font.SysFont("comicsansms", 30)
        self.clock = pygame.time.Clock()
        self.reset()

    def reset(self):
        # reset game parameters
        self.game_over = False
        self.direction = Direction.RIGHT
        self.x = self.scr_width // 2
        self.y = self.scr_height // 2
        self.snake_list = []
        self.snake_length = 1
        self.place_food()
        self.frame_iteration = 0

    def place_food(self):
        self.food_x = round(random.randrange(0, self.scr_width - 1))
        self.food_y = round(random.randrange(0, self.scr_height - 1))

    # TODO delete
    """
    def message(msg, color):
        text = FontStyle.render(msg, True, color)
        dis.blit(text, [SCR_WIDTH * SCALING_FACTOR // 6, SCR_HEIGHT * SCALING_FACTOR // 2])
    """

    def draw_snake(self):
        for snake_part in self.snake_list:
            pygame.draw.rect(self.screen, BLACK,
                             [snake_part[0], snake_part[1], 1, 1])

    def redraw(self):
        # draw on screen food, snake
        self.screen.fill(WHITE)
        pygame.draw.rect(self.screen, BLUE, [self.food_x, self.food_y, 1, 1])
        self.draw_snake()
        # transform from screen to display
        self.dis.blit(pygame.transform.scale(self.screen,
                                             self.dis.get_rect().size), (0, 0))
        scores = self.score_font.render("Your Score: " +
                                        str(self.snake_length - 1), True, RED)
        self.dis.blit(scores, [0, 0])
        pygame.display.update()  # TODO comment so supress screen

    def get_direction(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.direction = Direction.DOWN

    def get_direction_ai(self, action):
        # action = straight, turn_right, turn_left
        directions_cw = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
        direction_idx = directions_cw.index(self.direction)
        if np.array_equal(action, [1, 0, 0]):
            pass
        elif np.array_equal(action, [0, 1, 0]):
            direction_idx += 1
        elif np.array_equal(action, [0, 0, 1]):
            direction_idx -= 1
        else:
            print('Error action type')
        direction_idx %= 4
        self.direction = directions_cw[direction_idx]

    def is_collision(self, point=None):
        if point is None:
            point = [self.x, self.y]
        # in walls
        if point[0] < 0 or point[0] >= self.scr_width or \
                point[1] < 0 or point[1] >= self.scr_height:
            return True

        # in self (snake)
        for snake_part in self.snake_list[:-1]:  # except head to head
            if snake_part == (point[0], point[1]):
                return True
        return False

    def game_step(self, action=None):
        reward = 0
        self.frame_iteration += 1

        # 1. collect user input
        # self.set_direction()  # for player action INCLUDING quit
        self.get_direction_ai(action)  # for AI agent
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move
        self.move_step()

        # 3. check if game over
        if self.is_collision() or self.frame_iteration > 200 * self.snake_length:
            reward = -10
            self.game_over = True
            return reward, self.game_over, self.snake_length - 1

        # 4. place new food or just move
        reward = self.check_food(reward)

        # 5. update ui and clock
        self.redraw()
        self.clock.tick(self.snake_speed)
        return reward, self.game_over, self.snake_length - 1

    def check_food(self, reward):
        if self.x == self.food_x and self.y == self.food_y:
            reward = 20
            self.place_food()
            self.snake_length = self.snake_length + 1
        self.snake_list.append((self.x, self.y))
        if len(self.snake_list) > self.snake_length:
            del self.snake_list[0]
        return reward

    def move_step(self):
        if self.direction == Direction.LEFT:
            self.x = self.x - 1
        elif self.direction == Direction.RIGHT:
            self.x = self.x + 1
        elif self.direction == Direction.UP:
            self.y = self.y - 1
        elif self.direction == Direction.DOWN:
            self.y = self.y + 1

    def game_loop(self):

        while not self.game_over:
            self.game_step()

        # game is over
        return self.snake_length - 1
        # message("You Lost. q - quit, p - play again", RED)
        # pygame.display.update()


if __name__ == '__main__':
    # program constants
    SCR_WIDTH = 40  # screen size
    SCR_HEIGHT = 30
    SCALING_FACTOR = 20  # screen to display
    SNAKE_SPEED = 10

    game = SnakeGameAI(SNAKE_SPEED, SCR_WIDTH, SCR_HEIGHT, SCALING_FACTOR)
    score = game.game_loop()
    print(f"Score: {score}")
    pass

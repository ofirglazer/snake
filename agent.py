import torch
import random
import numpy as np
from collections import deque
from snake_game import SnakeGameAI, Direction
from model import Linear_QNet, QTrainer
from plot import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001


class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0  # randomness
        self.gamma = 0.9  # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # pop left
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    @staticmethod
    def get_state(game):
        head = [game.x, game.y]
        point_l = [head[0] - 1, head[1]]
        point_r = [head[0] + 1, head[1]]
        point_u = [head[0], head[1] - 1]
        point_d = [head[0], head[1] + 1]

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # straight collision
            (dir_l and game.is_collision(point_l) or
             dir_r and game.is_collision(point_r) or
             dir_u and game.is_collision(point_u) or
             dir_d and game.is_collision(point_d)),

            # right collision
            (dir_l and game.is_collision(point_u) or
             dir_r and game.is_collision(point_d) or
             dir_u and game.is_collision(point_r) or
             dir_d and game.is_collision(point_l)),

            # left collision
            (dir_l and game.is_collision(point_d) or
             dir_r and game.is_collision(point_u) or
             dir_u and game.is_collision(point_l) or
             dir_d and game.is_collision(point_r)),

            # move direction
            dir_l, dir_r, dir_u, dir_d,

            # food relative location
            game.food_x < head[0],  # food is left to head
            game.food_x > head[0],  # food is right to head
            game.food_y < head[0],  # food is up to head
            game.food_y > head[0]]  # food is down to head

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))
        # pop left if MAX_MEMORY reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, game_overs = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
        # tradeoff between exploration and exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            # random exploration
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            # prediction exploitation
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()

    while True:

        # get old state
        old_state = agent.get_state(game)

        # set move
        final_move = agent.get_action(old_state)
        # if final_move == 0:
        #     move_command = 'straight'
        # elif final_move == 1:
        #     move_command = 'turn_right'
        # else:
        #     move_command = 'turn_left'

        # perform move and get new state
        reward, game_over, score = game.game_step(final_move)
        new_state = agent.get_state(game)
        # train short memory
        agent.train_short_memory(old_state, final_move, reward, new_state, game_over)
        # remember
        agent.remember(old_state, final_move, reward, new_state, game_over)

        if game_over:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()
            if score > record:
                record = score
                agent.model.save()
            print(f"Game {agent.n_games} score: {score}, record: {record}")

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()

import numpy as np
import sys
sys.path.append('')
import c4dynamics as c4d
import random
import matplotlib.pyplot as plt

# Define the Environment and State
class SimpleEnv:
    def __init__(self, target):
        self.target = np.array(target)
        self.state = c4d.state(x=0, y=0)

    def reset(self):
        self.state = c4d.state(x=0, y=0)
        return self.state.X.astype(int)

    def step(self, action):
        # Actions: 0=up, 1=down, 2=left, 3=right
        if action == 0:
            self.state.x += 1
        elif action == 1:
            self.state.x -= 1
        elif action == 2:
            self.state.y -= 1
        elif action == 3:
            self.state.y += 1

        done = np.array_equal(self.state.X, self.target)
        reward = -1 if not done else 0

        return self.state.X.astype(int), reward, done

env = SimpleEnv(target=[5, 5])

# Define the state and action space
state_space = (10, 10)
action_space = 4  # Up, down, left, right

# Initialize Q-table with zeros
Q_table = np.zeros(state_space + (action_space,))

# Hyperparameters
alpha = 0.1  # Learning rate
gamma = 0.99  # Discount factor
epsilon = 1.0  # Exploration rate
epsilon_decay = 0.995
min_epsilon = 0.01
episodes = 1000

def choose_action(state):
    if random.uniform(0, 1) < epsilon:
        return random.randint(0, action_space - 1)
    else:
        return np.argmax(Q_table[state[0], state[1], :])

# Training the agent
for episode in range(episodes):
    state = env.reset()
    done = False

    while not done:
        action = choose_action(state)
        next_state, reward, done = env.step(action)
        old_value = Q_table[state[0], state[1], action]
        next_max = np.max(Q_table[next_state[0], next_state[1], :])

        # Update Q-value
        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        Q_table[state[0], state[1], action] = new_value

        state = next_state

    # Decay the exploration rate
    if epsilon > min_epsilon:
        epsilon *= epsilon_decay

# Visualize the Results
state = env.reset()
done = False
path = [state]

while not done:
    action = np.argmax(Q_table[state[0], state[1], :])
    state, _, done = env.step(action)
    path.append(state)

# Convert path to array for plotting
path = np.array(path)

# Plot the path
plt.plot(path[:, 0], path[:, 1], marker='o')
plt.scatter(env.target[0], env.target[1], marker='x', color='red', label='Target')
plt.title('Agent Path to Target')
plt.xlabel('X')
plt.ylabel('Y')
plt.legend()
plt.grid()
plt.show()

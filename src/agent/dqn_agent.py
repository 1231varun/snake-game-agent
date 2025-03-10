"""
Deep Q-Network (DQN) Agent for Snake Game
"""

import os
import random
import time
from collections import deque

import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

# Optimize TensorFlow for Apple Silicon if available
if hasattr(tf.config, "experimental"):
    try:
        physical_devices = tf.config.experimental.list_physical_devices("GPU")
        if physical_devices:
            tf.config.experimental.set_memory_growth(physical_devices[0], True)
    except Exception:
        pass

# Enable Metal plugin for Apple Silicon (M1/M2/M3)
is_apple_silicon = False
try:
    import platform

    if platform.machine() == "arm64" and platform.system() == "Darwin":
        is_apple_silicon = True
        os.environ["TF_ENABLE_ONEDNN_OPTS"] = "1"
        print("Apple Silicon detected - optimizations enabled")
        # Set mixed precision policy if on Apple Silicon
        if hasattr(tf.keras.mixed_precision, "set_global_policy"):
            tf.keras.mixed_precision.set_global_policy("mixed_float16")
except Exception:
    pass


class DQNAgent:
    """
    DQN Agent for playing snake game
    Uses Deep Q-Network with experience replay and target network
    """

    def __init__(
        self,
        state_size=11,  # 11 features in our simplified state
        action_size=3,  # 0=straight, 1=right, 2=left
        memory_size=10000,
        gamma=0.95,  # discount factor
        epsilon=1.0,  # exploration rate
        epsilon_min=0.01,
        epsilon_decay=0.99,  # Faster decay for quicker learning
        learning_rate=0.001,
        batch_size=64,
        update_target_freq=5,
    ):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=memory_size)
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.update_target_freq = update_target_freq

        # Main Q-network
        self.model = self._build_model()

        # Target Q-network for stable training
        self.target_model = self._build_model()
        self.update_target_model()

        # Training metrics
        self.train_count = 0
        self.losses = []

        # Add timestamp for unique model naming
        self.start_time = int(time.time())

    def _build_model(self):
        """Build the neural network model."""
        # Use a smaller batch size for faster iterations on M3
        model = Sequential(
            [
                # Larger network for better learning
                Dense(32, input_dim=self.state_size, activation="relu"),
                Dropout(0.1),  # Add dropout for regularization
                Dense(64, activation="relu"),
                Dropout(0.1),
                Dense(32, activation="relu"),
                Dense(self.action_size, activation="linear"),
            ]
        )

        # Use a higher learning rate on Apple Silicon for faster training
        lr = 0.002 if is_apple_silicon else self.learning_rate

        model.compile(loss="mse", optimizer=Adam(learning_rate=lr))
        return model

    def update_target_model(self):
        """Copy weights from main model to target model."""
        self.target_model.set_weights(self.model.get_weights())

    def remember(self, state, action, reward, next_state, done):
        """Add experience to memory."""
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, explore=True):
        """Choose an action based on the current state."""
        # Exploration: choose a random action
        if explore and np.random.rand() <= self.epsilon:
            # Occasionally use targeted exploration: If food is detected, bias
            # towards trying to move in that direction
            if state[7:11].any():  # Food direction detected (any of indices 7-10 is True)
                # Find which direction(s) have food
                food_dirs = []
                if state[7]:  # Food left
                    food_dirs.append(2)  # Left turn
                if state[8]:  # Food right
                    food_dirs.append(1)  # Right turn
                if state[9] or state[10]:  # Food up or down, might need straight
                    food_dirs.append(0)  # Straight

                # 75% chance to move towards food when exploring
                if food_dirs and random.random() < 0.75:
                    return random.choice(food_dirs)

            # Otherwise choose fully random
            return random.randrange(self.action_size)

        # Exploitation: choose best action from Q-values
        # Use a batched prediction for better performance on M3
        act_values = self.model.predict(state.reshape(1, -1), verbose=0)
        return np.argmax(act_values[0])

    def replay(self):
        """Train the agent on random samples from memory."""
        if len(self.memory) < self.batch_size:
            return 0  # Not enough samples for training

        # Sample a batch from memory
        minibatch = random.sample(self.memory, self.batch_size)

        # Prepare batches for more efficient training on M3
        states = np.zeros((self.batch_size, self.state_size))
        targets = np.zeros((self.batch_size, self.action_size))

        for i, (state, action, reward, next_state, done) in enumerate(minibatch):
            # Current Q-value from main model
            target = self.model.predict(state.reshape(1, -1), verbose=0)[0]

            if done:
                # For terminal states, the target is just the reward
                target[action] = reward
            else:
                # For non-terminal states, target is reward + gamma * max future Q-value
                # Using the target model for stability
                next_q_values = self.target_model.predict(next_state.reshape(1, -1), verbose=0)[0]
                target[action] = reward + self.gamma * np.amax(next_q_values)

            states[i] = state
            targets[i] = target

        # Train the model in a single batch for better performance
        history = self.model.fit(states, targets, epochs=1, verbose=0, batch_size=self.batch_size)
        loss = history.history["loss"][0]
        self.losses.append(loss)

        # Decay epsilon for less exploration over time
        if self.epsilon > self.epsilon_min:
            # Use a more aggressive decay at the beginning
            if self.train_count < 100:
                # Fast decay for first 100 training steps
                self.epsilon *= 0.98
            else:
                # Normal decay after that
                self.epsilon *= self.epsilon_decay

        # Update target model periodically
        self.train_count += 1
        if self.train_count % self.update_target_freq == 0:
            self.update_target_model()

        return loss

    def load(self, name):
        """Load model weights from disk."""
        self.model.load_weights(name)
        self.target_model.load_weights(name)

    def save(self, name):
        """Save model weights to disk."""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(name), exist_ok=True)
        self.model.save_weights(name)

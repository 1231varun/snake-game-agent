"""
Deep Q-Network (DQN) Agent for Snake Game
"""
import os
import random
import numpy as np
from collections import deque
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

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
        gamma=0.95,     # discount factor
        epsilon=1.0,    # exploration rate
        epsilon_min=0.01,
        epsilon_decay=0.995,
        learning_rate=0.001,
        batch_size=64,
        update_target_freq=5
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
    
    def _build_model(self):
        """Build the neural network model."""
        model = Sequential([
            Dense(24, input_dim=self.state_size, activation='relu'),
            Dense(24, activation='relu'),
            Dense(self.action_size, activation='linear')
        ])
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
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
            return random.randrange(self.action_size)
        
        # Exploitation: choose best action from Q-values
        act_values = self.model.predict(state.reshape(1, -1), verbose=0)
        return np.argmax(act_values[0])
    
    def replay(self):
        """Train the agent on random samples from memory."""
        if len(self.memory) < self.batch_size:
            return 0  # Not enough samples for training
        
        # Sample a batch from memory
        minibatch = random.sample(self.memory, self.batch_size)
        
        x = []  # states
        y = []  # target Q-values
        
        for state, action, reward, next_state, done in minibatch:
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
            
            x.append(state)
            y.append(target)
        
        # Train the model
        history = self.model.fit(
            np.array(x), np.array(y), 
            epochs=1, verbose=0, batch_size=self.batch_size
        )
        loss = history.history['loss'][0]
        self.losses.append(loss)
        
        # Decay epsilon for less exploration over time
        if self.epsilon > self.epsilon_min:
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
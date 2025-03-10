"""
Trainer for the Snake Game agent
"""
import os
import time
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from agent.dqn_agent import DQNAgent
from game.snake import SnakeGame

class SnakeTrainer:
    """
    Trainer for the Snake Game agent
    """
    
    def __init__(
        self,
        model_name="models/snake_dqn.h5",
        log_dir="data",
        episodes=1000,
        max_steps=2000,
        batch_size=64,
        target_update_freq=5,
        save_freq=100,
        render_freq=0  # 0 means no rendering during training
    ):
        self.model_name = model_name
        self.log_dir = log_dir
        self.episodes = episodes
        self.max_steps = max_steps
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.save_freq = save_freq
        self.render_freq = render_freq
        
        # Create directories
        os.makedirs(os.path.dirname(model_name), exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)
        
        # Initialize agent and environment
        self.game = SnakeGame()
        self.agent = DQNAgent(
            state_size=11,
            action_size=3,
            batch_size=batch_size,
            update_target_freq=target_update_freq
        )
        
        # Training metrics
        self.scores = []
        self.avg_scores = []
        self.epsilons = []
        self.losses = []
    
    def train(self):
        """Train the agent."""
        print("Starting training...")
        
        for e in tqdm(range(self.episodes)):
            # Reset environment and agent metrics
            state = self.game.reset()
            state = self.game.get_state_for_agent()
            
            score = 0
            episode_loss = []
            
            for step in range(self.max_steps):
                # Decide action
                action = self.agent.act(state)
                
                # Take action
                next_state_dict, reward, done, info = self.game.step(action)
                next_state = self.game.get_state_for_agent()
                
                # Remember experience
                self.agent.remember(state, action, reward, next_state, done)
                
                # Set current state to next state
                state = next_state
                
                # Update score
                score += reward
                
                # Train the model (experience replay)
                if len(self.agent.memory) > self.batch_size:
                    loss = self.agent.replay()
                    episode_loss.append(loss)
                
                # Render if required
                if self.render_freq > 0 and e % self.render_freq == 0:
                    self.game.render()
                    time.sleep(0.01)  # Small delay for visualization
                
                if done:
                    break
            
            # Store metrics
            self.scores.append(info["score"])
            avg_score = np.mean(self.scores[-100:])  # Moving average of last 100 episodes
            self.avg_scores.append(avg_score)
            self.epsilons.append(self.agent.epsilon)
            
            if episode_loss:
                self.losses.append(np.mean(episode_loss))
            
            # Print progress
            template = "Episode: {:4d}/{:4d} | Score: {:3d} | Avg Score: {:5.2f} | Epsilon: {:.4f}"
            print(template.format(e+1, self.episodes, info["score"], avg_score, self.agent.epsilon))
            
            # Save the model periodically
            if self.save_freq > 0 and (e+1) % self.save_freq == 0:
                model_path = f"{self.model_name.replace('.h5', '')}_{e+1}.h5"
                self.agent.save(model_path)
                print(f"Model saved to {model_path}")
                
                # Plot and save metrics
                self.plot_metrics(save=True, episode=e+1)
        
        # Save the final model
        self.agent.save(self.model_name)
        print(f"Final model saved to {self.model_name}")
        
        # Plot final metrics
        self.plot_metrics(save=True)
        
        return self.agent
    
    def plot_metrics(self, save=False, episode=None):
        """Plot training metrics."""
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))
        
        # Plot scores
        ax1.plot(self.scores, label='Score', alpha=0.6)
        ax1.plot(self.avg_scores, label='Avg Score (100 episodes)', linewidth=2)
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Score')
        ax1.set_title('Score over Episodes')
        ax1.legend()
        ax1.grid(True, linestyle='--', alpha=0.7)
        
        # Plot epsilon
        ax2.plot(self.epsilons)
        ax2.set_xlabel('Episode')
        ax2.set_ylabel('Epsilon')
        ax2.set_title('Exploration Rate (Epsilon) over Episodes')
        ax2.grid(True, linestyle='--', alpha=0.7)
        
        # Plot loss
        if self.losses:
            ax3.plot(self.losses)
            ax3.set_xlabel('Episode')
            ax3.set_ylabel('Loss')
            ax3.set_title('Average Loss per Episode')
            ax3.grid(True, linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        if save:
            suffix = f"_ep{episode}" if episode else ""
            plt.savefig(f"{self.log_dir}/training_metrics{suffix}.png")
            
            # Save data to CSV
            np.savetxt(f"{self.log_dir}/scores{suffix}.csv", np.array(self.scores), delimiter=',')
            np.savetxt(f"{self.log_dir}/avg_scores{suffix}.csv", np.array(self.avg_scores), delimiter=',')
            if self.losses:
                np.savetxt(f"{self.log_dir}/losses{suffix}.csv", np.array(self.losses), delimiter=',')
        else:
            plt.show()
    
    def test(self, model_path=None, episodes=10, render=True, fps=5):
        """Test a trained agent."""
        if model_path:
            self.agent.load(model_path)
            print(f"Loaded model from {model_path}")
        elif os.path.exists(self.model_name):
            self.agent.load(self.model_name)
            print(f"Loaded model from {self.model_name}")
        else:
            print("No model found, using untrained agent")
        
        scores = []
        
        for e in range(episodes):
            state = self.game.reset()
            state = self.game.get_state_for_agent()
            
            done = False
            steps = 0
            
            while not done:
                # Choose action without exploration
                action = self.agent.act(state, explore=False)
                
                # Take action
                next_state_dict, reward, done, info = self.game.step(action)
                next_state = self.game.get_state_for_agent()
                
                state = next_state
                steps += 1
                
                if render:
                    frame = self.game.render()
                    self.game.tick(fps)
                
                if done:
                    scores.append(info["score"])
                    print(f"Episode {e+1}/{episodes} | Score: {info['score']} | Steps: {steps}")
                    break
        
        avg_score = np.mean(scores)
        print(f"Average Score over {episodes} episodes: {avg_score:.2f}")
        return scores 
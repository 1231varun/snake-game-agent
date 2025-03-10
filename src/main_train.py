#!/usr/bin/env python
"""
Snake Game Agent - Training Entry Point
Trains the RL agent to play snake game
"""
import argparse
import os
from agent.trainer import SnakeTrainer

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Train Snake Game RL Agent')
    parser.add_argument('--episodes', type=int, default=1000,
                        help='Number of episodes to train')
    parser.add_argument('--model', type=str, default='models/snake_dqn.h5',
                        help='Path to save the trained model')
    parser.add_argument('--render-freq', type=int, default=0,
                        help='Frequency of rendering during training (0 for no rendering)')
    parser.add_argument('--save-freq', type=int, default=100,
                        help='Frequency of saving checkpoints during training')
    parser.add_argument('--batch-size', type=int, default=64,
                        help='Batch size for training')
    parser.add_argument('--max-steps', type=int, default=2000,
                        help='Maximum steps per episode')
    return parser.parse_args()

def main():
    """Main function to run training."""
    args = parse_args()
    
    print("Starting Snake Game RL Agent Training...")
    print(f"Training for {args.episodes} episodes")
    print(f"Model will be saved to {args.model}")
    
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(args.model), exist_ok=True)
    
    # Create and run the trainer
    trainer = SnakeTrainer(
        model_name=args.model,
        episodes=args.episodes,
        max_steps=args.max_steps,
        batch_size=args.batch_size,
        save_freq=args.save_freq,
        render_freq=args.render_freq
    )
    
    # Start training
    agent = trainer.train()
    
    print("Training completed!")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python
"""
Snake Game Agent - Training Entry Point
Trains the RL agent to play snake game
"""
import argparse
import os
import platform
import time

from agent.trainer import SnakeTrainer


def parse_args():
    """Parse command line arguments."""
    # Set optimized defaults for M3
    is_apple_silicon = platform.machine() == "arm64" and platform.system() == "Darwin"

    # Smaller defaults for M3 to get faster iterations
    default_episodes = 500 if is_apple_silicon else 1000
    default_batch_size = 32 if is_apple_silicon else 64
    default_max_steps = 500 if is_apple_silicon else 2000
    default_timeout = 50 if is_apple_silicon else 100  # Timeout multiplier

    parser = argparse.ArgumentParser(description="Train Snake Game RL Agent")
    parser.add_argument("--episodes", type=int, default=default_episodes, help="Number of episodes to train")
    parser.add_argument("--model", type=str, default="models/snake_dqn.h5", help="Path to save the trained model")
    parser.add_argument(
        "--render-freq", type=int, default=0, help="Frequency of rendering during training (0 for no rendering)"
    )
    parser.add_argument(
        "--save-freq",
        type=int,
        default=max(20, default_episodes // 10),
        help="Frequency of saving checkpoints during training",
    )
    parser.add_argument("--batch-size", type=int, default=default_batch_size, help="Batch size for training")
    parser.add_argument("--max-steps", type=int, default=default_max_steps, help="Maximum steps per episode")
    parser.add_argument(
        "--timeout", type=int, default=default_timeout, help="Timeout multiplier for steps without food"
    )
    parser.add_argument(
        "--continue",
        dest="continue_training",
        action="store_true",
        help="Continue training from existing model if available",
    )
    parser.add_argument(
        "--fresh",
        dest="continue_training",
        action="store_false",
        help="Start with a fresh model, ignoring any existing one",
    )
    parser.set_defaults(continue_training=True)
    return parser.parse_args()


def main():
    """Main function to run training."""
    args = parse_args()

    print("Starting Snake Game RL Agent Training...")
    print(f"Training for {args.episodes} episodes")
    print(f"Model will be saved to {args.model}")
    print(f"Continue from existing model: {args.continue_training}")

    # Print hardware information
    print(f"Running on {platform.machine()} processor")
    if platform.machine() == "arm64" and platform.system() == "Darwin":
        print("Apple Silicon detected - using optimized training parameters")

    # Create directories if they don't exist
    os.makedirs(os.path.dirname(args.model), exist_ok=True)

    # Record start time
    start_time = time.time()

    # Create and run the trainer
    trainer = SnakeTrainer(
        model_name=args.model,
        episodes=args.episodes,
        max_steps=args.max_steps,
        batch_size=args.batch_size,
        save_freq=args.save_freq,
        render_freq=args.render_freq,
        timeout_multiplier=args.timeout,
        continue_training=args.continue_training,
    )

    # Start training
    trainer.train()

    # Print training duration
    duration = time.time() - start_time
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"Training completed in {int(hours)}h {int(minutes)}m {int(seconds)}s")
    print(f"Final model saved to {args.model}")


if __name__ == "__main__":
    main()

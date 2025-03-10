#!/usr/bin/env python
"""
Snake Game Agent - Visual Training Entry Point
Trains the RL agent to play snake game with web-based visualization
"""
import argparse
import os
import platform
import threading
import time

import numpy as np
from flask import Flask, jsonify, render_template, request

from agent.trainer import SnakeTrainer
from game.snake import SnakeGame

# Initialize Flask app
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),
    template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"),
)
app.config["SECRET_KEY"] = "snakegamevisualsecret!"

# Global state to track training
training_state = {
    "running": False,
    "paused": False,
    "episode": 0,
    "total_episodes": 0,
    "score": 0,
    "avg_score": 0.0,
    "epsilon": 1.0,
    "step": 0,
    "total_steps": 0,
    "timeouts": 0,
    "game_state": None,
    "frame_base64": None,
    "losses": [],
    "scores": [],
    "avg_scores": [],
    "epsilons": [],
    "last_update": time.time(),
    "log_messages": [],  # Queue for log messages
}

# Max number of log messages to keep
MAX_LOG_MESSAGES = 100


def add_log_message(message):
    """Add a log message to the training state"""
    training_state["log_messages"].append({"timestamp": time.strftime("%H:%M:%S"), "message": message})
    # Keep only the last MAX_LOG_MESSAGES
    if len(training_state["log_messages"]) > MAX_LOG_MESSAGES:
        training_state["log_messages"] = training_state["log_messages"][-MAX_LOG_MESSAGES:]
    # Also print to console for debugging
    print(f"[LOG] {message}")


# Paths for templates and static files
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(template_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)
os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)

# Create simple CSS file
with open(os.path.join(static_dir, "style.css"), "w", encoding="utf-8") as f:
    f.write(
        """
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}
    """
    )


# Flask routes
@app.route("/")
def index():
    """Main visualization page"""
    return render_template("visual_training.html")


@app.route("/api/state")
def get_state():
    """Return current training state as JSON"""
    return jsonify(training_state)


@app.route("/api/log", methods=["POST"])
def add_external_log():
    """Add an external log message (from client)"""
    data = request.json
    message = data.get("message")
    if message:
        add_log_message(message)
        return jsonify({"status": "ok", "message": "Log added successfully"})
    return jsonify({"status": "error", "message": "No message provided"}), 400


@app.route("/api/control", methods=["POST"])
def control():
    """Handle control commands from the web interface"""
    data = request.json
    command = data.get("command")
    if command == "pause":
        training_state["paused"] = True
        add_log_message("Training paused by user")
    elif command == "resume":
        training_state["paused"] = False
        add_log_message("Training resumed by user")
    elif command == "speed":
        # Speed value is handled in the training loop
        value = data.get("value", 1.0)
        training_state["speed"] = value
        add_log_message(f"Speed changed to {value}x")
    return jsonify({"status": "ok"})


class VisualTrainer(SnakeTrainer):
    """Extended trainer with visualization capabilities"""

    def __init__(self, *args, **kwargs):
        # Extract web-specific parameters
        self.speed = 1.0
        self.paused = False
        self.port = kwargs.pop("port", 3000)

        # Initialize parent class
        super().__init__(*args, **kwargs)

        # Override game to capture frames
        self.game = SnakeGame(max_steps_without_food=self.timeout_multiplier)

    def update_training_state(self, episode, step, info=None):
        """Update the training state for visualization"""
        import base64
        import io

        import pygame

        # Skip updates if too frequent
        current_time = time.time()
        if current_time - training_state["last_update"] < 0.05:  # Max 20 updates per second
            return

        # Render the current game state to a surface
        surface = self.game.render()

        # Convert Pygame surface to base64 image
        buffer = io.BytesIO()
        pygame.image.save(surface, buffer, "PNG")
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode("utf-8")

        # Get event information
        if info and info.get("done", False):
            pass  # Empty block instead of removed variable

        # Log significant events
        if episode > 0 and episode != training_state["episode"]:
            add_log_message(f"Starting episode {episode + 1}/{self.episodes}")

        if info:
            if info.get("ate_food", False):
                add_log_message(f"Episode {episode + 1}: Snake ate food! Score: {info.get('score', 0)}")

            if info.get("done", False):
                if info.get("timeout", False):
                    add_log_message(f"Episode {episode + 1} timeout. Final score: {info.get('score', 0)}")
                elif info.get("collision", False):
                    add_log_message(
                        f"Episode {episode + 1} ended - Snake collision. Final score: {info.get('score', 0)}"
                    )

        # Update training state
        training_state.update(
            {
                "running": True,
                "paused": self.paused,
                "episode": episode + 1,
                "total_episodes": self.episodes,
                "score": info.get("score", 0) if info else 0,
                "avg_score": np.mean(self.scores[-100:]) if self.scores else 0.0,
                "epsilon": self.agent.epsilon,
                "step": step,
                "total_steps": self.game.total_steps,
                "timeouts": self.timeout_count,
                "frame_base64": img_base64,
                "last_update": current_time,
            }
        )

        # Update chart data if episode changed
        if episode >= len(training_state["scores"]):
            training_state["scores"].append(info.get("score", 0) if info else 0)
            training_state["avg_scores"].append(np.mean(self.scores[-100:]) if self.scores else 0.0)
            training_state["epsilons"].append(self.agent.epsilon)

    def train(self):
        """Train the agent with visualization"""
        print("Starting visual training...")
        add_log_message("Starting visual training...")
        add_log_message(f"Training for {self.episodes} episodes")
        add_log_message(f"Model will be saved as {self.model_name}")
        print(f"Timeout multiplier: {self.timeout_multiplier}")
        add_log_message(f"Timeout multiplier: {self.timeout_multiplier}")

        # Calculate how often to print progress - handling small episode counts
        print_freq = max(1, self.episodes // 10) if self.episodes > 1 else 1

        for e in range(self.episodes):
            episode_start = time.time()

            # Reset environment and agent metrics
            state = self.game.reset()
            state = self.game.get_state_for_agent()

            score = 0
            episode_loss = []

            # Initial update for this episode
            self.update_training_state(e, 0)

            for step in range(self.max_steps):
                # Check if training is paused
                while training_state["paused"]:
                    time.sleep(0.1)

                # Decide action
                action = self.agent.act(state)

                # Take action
                _, reward, done, info = self.game.step(action)
                next_state = self.game.get_state_for_agent()

                # Remember experience
                self.agent.remember(state, action, reward, next_state, done)

                # Set current state to next state
                state = next_state

                # Update score
                score += reward

                # Update visualization
                self.update_training_state(e, step, info)

                # Train the model (experience replay)
                if len(self.agent.memory) > self.batch_size:
                    loss = self.agent.replay()
                    episode_loss.append(loss)

                # Control speed of visualization
                speed = training_state.get("speed", 1.0)
                if self.render_freq > 0 and e % self.render_freq == 0:
                    time.sleep(0.1 / speed)  # Adjust wait time based on speed

                if done:
                    # Track timeout events
                    if info.get("timeout", False):
                        self.timeout_count += 1
                        add_log_message(f"Episode {e + 1} timeout! Total timeouts: {self.timeout_count}")
                    break

            # Store metrics
            episode_duration = time.time() - episode_start
            self.episode_durations.append(episode_duration)
            self.scores.append(info["score"])
            avg_score = np.mean(self.scores[-100:])  # Moving average of last 100 episodes
            self.avg_scores.append(avg_score)
            self.epsilons.append(self.agent.epsilon)

            if episode_loss:
                self.losses.append(np.mean(episode_loss))

            # Print progress periodically
            if (e + 1) % print_freq == 0 or (e + 1) == self.episodes:
                template = "Episode: {:4d}/{:4d} | Score: {:3d} | Avg Score: {:5.2f} | Epsilon: {:.4f} | Timeouts: {:d}"
                log_message = template.format(
                    e + 1, self.episodes, info["score"], avg_score, self.agent.epsilon, self.timeout_count
                )
                print(log_message)
                add_log_message(log_message)

            # Save the model periodically
            if self.save_freq > 0 and (e + 1) % self.save_freq == 0:
                model_path = f"{self.model_name.replace('.h5', '')}_{e + 1}.h5"
                self.agent.save(model_path)
                save_msg = f"Model checkpoint saved to {model_path}"
                print(save_msg)
                add_log_message(save_msg)

                # Plot and save metrics
                self.plot_metrics(save=True, episode=e + 1)

                # Print performance stats
                elapsed = time.time() - self.start_time
                avg_time_per_episode = elapsed / (e + 1)
                estimated_time_left = avg_time_per_episode * (self.episodes - (e + 1))
                hours, remainder = divmod(estimated_time_left, 3600)
                minutes, seconds = divmod(remainder, 60)

                print(f"Average time per episode: {avg_time_per_episode:.2f}s")
                print(f"Estimated time remaining: {int(hours)}h {int(minutes)}m {int(seconds)}s")
                print(
                    f"Timeout events: {self.timeout_count}/{e + 1} episodes ({(self.timeout_count / (e + 1)) * 100:.1f}%)"
                )

        # Save the final model
        self.agent.save(self.model_name)
        print(f"Final model saved to {self.model_name}")

        # Plot final metrics
        self.plot_metrics(save=True)

        # Final stats
        total_time = time.time() - self.start_time
        hours, remainder = divmod(total_time, 3600)
        minutes, seconds = divmod(remainder, 60)

        print(f"Total training time: {int(hours)}h {int(minutes)}m {int(seconds)}s")
        print(f"Average time per episode: {total_time / self.episodes:.2f}s")
        print(
            f"Timeout events: {self.timeout_count}/{self.episodes} episodes ({(self.timeout_count / self.episodes) * 100:.1f}%)"
        )

        # Update training state to indicate completion
        training_state["running"] = False

        return self.agent


def parse_args():
    """Parse command line arguments."""
    # Set optimized defaults for M3
    is_apple_silicon = platform.machine() == "arm64" and platform.system() == "Darwin"

    # Medium defaults for visual training
    default_episodes = 50 if is_apple_silicon else 100
    default_batch_size = 32 if is_apple_silicon else 64
    default_max_steps = 250 if is_apple_silicon else 500
    default_timeout = 40 if is_apple_silicon else 80  # Timeout multiplier
    default_port = int(os.environ.get("SNAKE_GAME_WEB_PORT", 3000))

    parser = argparse.ArgumentParser(description="Visual Train Snake Game RL Agent")
    parser.add_argument("--episodes", type=int, default=default_episodes, help="Number of episodes to train")
    parser.add_argument("--model", type=str, default="models/visual_model.h5", help="Path to save the trained model")
    parser.add_argument(
        "--render-freq", type=int, default=1, help="Frequency of rendering during training (0 for no rendering)"
    )
    parser.add_argument(
        "--save-freq",
        type=int,
        default=max(5, default_episodes // 10),
        help="Frequency of saving checkpoints during training",
    )
    parser.add_argument("--batch-size", type=int, default=default_batch_size, help="Batch size for training")
    parser.add_argument("--max-steps", type=int, default=default_max_steps, help="Maximum steps per episode")
    parser.add_argument(
        "--timeout", type=int, default=default_timeout, help="Timeout multiplier for steps without food"
    )
    parser.add_argument("--port", type=int, default=default_port, help="Web server port")
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

    print("Starting Snake Game RL Visual Training...")
    print(f"Training for {args.episodes} episodes")
    print(f"Model will be saved to {args.model}")
    print(f"Web interface available at http://localhost:{args.port}")
    print(f"Continue from existing model: {args.continue_training}")

    # Print hardware information
    print(f"Running on {platform.machine()} processor")
    if platform.machine() == "arm64" and platform.system() == "Darwin":
        print("Apple Silicon detected - using optimized training parameters")

    # Create directories if they don't exist
    os.makedirs(os.path.dirname(args.model), exist_ok=True)

    # Create the trainer
    trainer = VisualTrainer(
        model_name=args.model,
        episodes=args.episodes,
        max_steps=args.max_steps,
        batch_size=args.batch_size,
        save_freq=args.save_freq,
        render_freq=args.render_freq,
        timeout_multiplier=args.timeout,
        port=args.port,
        continue_training=args.continue_training,
    )

    # Start web server in a background thread
    def run_web_server():
        print(f"Starting web server on port {args.port}")
        try:
            app.run(host="0.0.0.0", port=args.port, debug=False, threaded=True)
        except Exception as e:
            print(f"Error starting server: {e}")

    webserver_thread = threading.Thread(target=run_web_server)
    webserver_thread.daemon = True
    webserver_thread.start()

    # Give the web server time to start
    time.sleep(2)

    # Start training
    print("Web server started. Training will begin shortly...")
    time.sleep(1)

    # Record start time
    start_time = time.time()

    # Run training
    trainer.train()

    # Print training duration
    duration = time.time() - start_time
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"Training completed in {int(hours)}h {int(minutes)}m {int(seconds)}s")
    print(f"Final model saved to {args.model}")

    # Keep the web server running for a short time to show final state
    print("Training completed. Web server will remain active for 60 seconds...")
    time.sleep(60)


if __name__ == "__main__":
    main()

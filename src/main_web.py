#!/usr/bin/env python
"""
Snake Game Agent - Web Interface Entry Point
Runs the game in a web browser
"""
import argparse
import os
import socket
import sys
import time

from game.webserver import run_web_server


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Snake Game with RL Agent (Web Interface)")
    parser.add_argument("--port", type=int, default=3000, help="Port to run the web server on")
    parser.add_argument(
        "--mode", type=str, default="human", choices=["human", "agent"], help="Mode to run the game: human or agent"
    )
    parser.add_argument(
        "--model", type=str, default="models/snake_dqn.h5", help="Path to the model file for agent mode"
    )
    parser.add_argument(
        "--episodes", type=int, default=1000, help="Number of episodes to train (for train mode in CLI)"
    )
    return parser.parse_args()


def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def main():
    """Main function to run the game."""
    args = parse_args()

    print("Running Snake Game with web interface...")
    print(f"Open your browser and go to http://localhost:{args.port} to play")

    # Validate model path for agent mode
    model_path = None
    if args.mode == "agent":
        if os.path.exists(args.model):
            model_path = args.model
            print(f"Using agent model: {model_path}")
        else:
            print(f"Warning: Model file {args.model} not found.")
            print("Running in human mode instead.")
            args.mode = "human"

    if args.mode == "human":
        print("Starting Snake game in human mode...")
    elif args.mode == "agent":
        print(f"Running agent with model: {model_path}")

    # In Docker, we might need to wait a moment for ports to clear
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Run the web server
            run_web_server(host="0.0.0.0", port=args.port, mode=args.mode, model_path=model_path)
            break
        except OSError as e:
            if "Address already in use" in str(e):
                retry_count += 1
                if retry_count < max_retries:
                    print(
                        f"\nPort {args.port} is busy. Waiting a moment for it to clear (attempt {retry_count}/{max_retries})..."
                    )
                    time.sleep(3)  # Wait a bit before retrying
                else:
                    print(f"\nERROR: Port {args.port} is already in use and could not be cleared.")
                    print("This could happen if:")
                    print("1. Another application is using this port")
                    print("2. A previous instance of the game is still running")
                    print("3. The port is reserved by your system")
                    print("\nTry using a different port with --port option.")
                    print("Example: python src/main_web.py --port 8080")
                    sys.exit(1)
            else:
                # Re-raise any other OSError
                raise


if __name__ == "__main__":
    main()

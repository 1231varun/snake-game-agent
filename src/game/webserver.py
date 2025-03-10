"""
Web server for the Snake Game - displays the game in a browser
"""
import os
import sys
import pygame
import io
import base64
import time
from flask import Flask, render_template, request, jsonify, Response, send_file
from threading import Thread
import json
from game.snake import SnakeGame

app = Flask(__name__)

# Game state
game_state = {
    "running": False,
    "frame": None,
    "command": None,
    "mode": "human",  # 'human' or 'agent'
    "agent": None,
    "model_path": None
}

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

class Button:
    """A simple button class for the menu."""
    
    def __init__(self, text, position, size=(200, 50), color=GREEN, hover_color=RED):
        self.text = text
        self.position = position
        self.size = size
        self.color = color
        self.hover_color = hover_color
        self.rect = pygame.Rect(position[0], position[1], size[0], size[1])
        self.is_hovered = False
        
    def draw(self, screen):
        """Draw the button on the screen."""
        # Draw button rectangle
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Border
        
        # Draw button text
        font = pygame.font.SysFont('Arial', 24)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def check_hover(self, mouse_pos):
        """Check if mouse is over the button."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        return self.is_hovered
        
    def is_clicked(self, mouse_pos):
        """Check if button is clicked."""
        return self.rect.collidepoint(mouse_pos)

def surface_to_base64(surface):
    """Convert a Pygame surface to base64 string for embedding in HTML."""
    image_data = pygame.image.tostring(surface, 'RGB')
    import io
    from PIL import Image
    image = Image.frombytes('RGB', surface.get_size(), image_data)
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return image_base64

def game_loop():
    """The main game loop that runs in a separate thread."""
    global game_state
    
    # Initialize pygame
    pygame.init()
    
    # Create the game
    game = SnakeGame()
    
    # Game clock
    clock = pygame.time.Clock()
    
    # For agent mode
    if game_state["mode"] == "agent" and game_state["model_path"]:
        from agent.dqn_agent import DQNAgent
        agent = DQNAgent()
        try:
            agent.load(game_state["model_path"])
            game_state["agent"] = agent
            print(f"Loaded agent model from {game_state['model_path']}")
        except Exception as e:
            print(f"Error loading agent model: {e}")
            game_state["mode"] = "human"
    
    # Main game loop
    game_state["running"] = True
    game_started = False
    restart_requested = False
    
    while game_state["running"]:
        # Process any commands from the web interface
        if game_state["command"]:
            command = game_state["command"]
            key = command.get("key")
            
            # Handle keyboard input
            if key:
                if key == "up" and game.direction != 2:
                    game.direction = 0  # UP
                elif key == "right" and game.direction != 3:
                    game.direction = 1  # RIGHT
                elif key == "down" and game.direction != 0:
                    game.direction = 2  # DOWN
                elif key == "left" and game.direction != 1:
                    game.direction = 3  # LEFT
                elif key == "r" and game.game_over:
                    restart_requested = True
                elif key == "space" and not game_started:
                    game_started = True
            
            # Reset the command
            game_state["command"] = None
            
        # Reset the game if requested
        if restart_requested:
            game.reset()
            restart_requested = False
            game_started = True
        
        # Update game state
        if game_started and not game.game_over:
            if game_state["mode"] == "agent" and game_state["agent"]:
                # Agent plays the game
                state = game.get_state_for_agent()
                action = game_state["agent"].act(state, explore=False)
                game.step(action)
            else:
                # Human plays the game
                game.step()
        
        # Render the game
        screen = game.render()
        
        # Show start screen if not started
        if not game_started:
            font = pygame.font.SysFont('Arial', 36)
            text = font.render('Press SPACE to start', True, (255, 255, 255))
            text_rect = text.get_rect(center=(game.width//2, game.height//2))
            screen.blit(text, text_rect)
            
            font = pygame.font.SysFont('Arial', 24)
            mode_text = font.render(f'Mode: {game_state["mode"].upper()}', True, (255, 255, 255))
            mode_rect = mode_text.get_rect(center=(game.width//2, game.height//2 + 50))
            screen.blit(mode_text, mode_rect)
            
            if game_state["mode"] == "agent":
                model_text = font.render(f'Model: {game_state["model_path"] or "None"}', True, (255, 255, 255))
                model_rect = model_text.get_rect(center=(game.width//2, game.height//2 + 80))
                screen.blit(model_text, model_rect)
        
        # Get base64 image of current screen
        game_state["frame"] = surface_to_base64(screen)
        
        # Cap at 10 FPS
        clock.tick(10)
    
    # Cleanup pygame
    pygame.quit()
    print("Game thread exiting")

@app.route('/')
def index():
    """Render the main game page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Snake Game</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                background-color: #f0f0f0;
                margin: 0;
                padding: 20px;
            }
            h1 {
                color: #333;
            }
            #game-container {
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                padding: 20px;
            }
            #game-screen {
                width: 800px;
                height: 600px;
                border: 1px solid #ccc;
                margin: 20px auto;
                cursor: pointer;
            }
            .controls {
                margin: 20px 0;
                padding: 10px;
                background-color: #f9f9f9;
                border-radius: 4px;
            }
            button {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                cursor: pointer;
                border-radius: 4px;
            }
            button:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <div id="game-container">
            <h1>Snake Game</h1>
            <img id="game-screen" src="" alt="Game Screen">
            <div class="controls">
                <p>Controls: Arrow keys to move, R to restart, SPACE to start</p>
                <p>Score will be displayed in the game window</p>
            </div>
        </div>
        
        <script>
            // Get the game screen element
            const gameScreen = document.getElementById('game-screen');
            
            // Function to update the game screen
            function updateGameScreen() {
                fetch('/get_frame')
                    .then(response => response.json())
                    .then(data => {
                        if (data.frame) {
                            gameScreen.src = 'data:image/png;base64,' + data.frame;
                        }
                    })
                    .catch(error => console.error('Error fetching frame:', error));
            }
            
            // Update the game screen every 100ms (approximately 10 FPS)
            setInterval(updateGameScreen, 100);
            
            // Handle keyboard input
            document.addEventListener('keydown', function(event) {
                let key = null;
                
                switch(event.key) {
                    case 'ArrowUp':
                        key = 'up';
                        break;
                    case 'ArrowRight':
                        key = 'right';
                        break;
                    case 'ArrowDown':
                        key = 'down';
                        break;
                    case 'ArrowLeft':
                        key = 'left';
                        break;
                    case 'r':
                    case 'R':
                        key = 'r';
                        break;
                    case ' ':
                        key = 'space';
                        break;
                }
                
                if (key) {
                    // Send key press to server
                    fetch('/send_command', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            key: key
                        })
                    });
                    
                    // Prevent default actions (like scrolling)
                    event.preventDefault();
                }
            });
        </script>
    </body>
    </html>
    """

@app.route('/get_frame', methods=['GET'])
def get_frame():
    """Return the current game frame as base64 encoded image."""
    return jsonify({"frame": game_state["frame"]})

@app.route('/send_command', methods=['POST'])
def send_command():
    """Receive commands from the web interface."""
    command = request.json
    game_state["command"] = command
    return jsonify({"status": "ok"})

@app.route('/set_mode', methods=['POST'])
def set_mode():
    """Set the game mode (human or agent)."""
    data = request.json
    mode = data.get('mode', 'human')
    model_path = data.get('model_path')
    
    if mode in ['human', 'agent']:
        game_state["mode"] = mode
        game_state["model_path"] = model_path
        return jsonify({"status": "ok", "mode": mode, "model_path": model_path})
    else:
        return jsonify({"status": "error", "message": "Invalid mode"})

def run_web_server(host='0.0.0.0', port=5000, mode='human', model_path=None):
    """Start the Flask web server."""
    # Set the game mode and model path
    game_state["mode"] = mode
    game_state["model_path"] = model_path
    
    # Start the game loop in a separate thread
    game_thread = Thread(target=game_loop)
    game_thread.daemon = True
    game_thread.start()
    
    # Run the Flask web server
    app.run(host=host, port=port, debug=False, threaded=True)
    
    # Wait for the game thread to finish
    game_state["running"] = False
    game_thread.join()

if __name__ == "__main__":
    run_web_server() 
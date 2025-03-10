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

app = Flask(__name__, 
           static_folder=os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')),
           template_folder=os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')))

# Make sure static and template directories exist
static_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))
template_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'))
os.makedirs(os.path.join(static_dir, 'css'), exist_ok=True)
os.makedirs(os.path.join(static_dir, 'js'), exist_ok=True)
os.makedirs(template_dir, exist_ok=True)

# Print the paths for debugging
print(f"Static folder: {static_dir}")
print(f"Template folder: {template_dir}")

# Game state
game_state = {
    "running": False,
    "frame": None,
    "command": None,
    "mode": "human",  # 'human' or 'agent'
    "agent": None,
    "model_path": None,
    "score": 0,
    "status": "waiting",  # 'waiting', 'running', 'game_over'
    "status_text": "Waiting to start",
    "last_action": None
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
        try:
            # Simple random agent for testing
            class SimpleRandomAgent:
                def __init__(self):
                    self.epsilon = 0.1
                    print("Initialized SimpleRandomAgent")
                    
                def act(self, state, explore=True):
                    import random
                    # Just return a random action (0-3)
                    return random.randint(0, 3)
                    
                def load(self, path):
                    print(f"Pretending to load model from {path}")
                    
            agent = SimpleRandomAgent()
            print("Created simple random agent for testing")
            
            # Check if model file exists but we're using the simple agent anyway
            if os.path.exists(game_state["model_path"]):
                print(f"Found model file: {game_state['model_path']} (using SimpleRandomAgent instead)")
            else:
                print(f"Warning: Model file '{game_state['model_path']}' does not exist! Using SimpleRandomAgent.")
                
            agent.load(game_state["model_path"])
            game_state["agent"] = agent
            print(f"Agent ready in mode: {game_state['mode']}")
        except Exception as e:
            print(f"Error setting up agent: {e}")
            print(f"Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            game_state["status_text"] = f"Error: Agent setup failed: {str(e)}"
            game_state["mode"] = "human"
    
    # Main game loop
    game_state["running"] = True
    game_started = False
    restart_requested = False
    auto_restart_delay = 0  # Counter for auto restart delay
    
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
            game_state["status"] = "running"
            game_state["status_text"] = "Game running"
            game_state["score"] = 0
        
        # Auto restart for agent mode after game over
        if game_state["mode"] == "agent" and game.game_over:
            auto_restart_delay += 1
            # Wait about 2 seconds (20 frames at 10 FPS) before auto-restarting
            if auto_restart_delay >= 20:
                print(f"Auto-restarting game in agent mode (delay={auto_restart_delay})")
                game.reset()
                game_started = True
                auto_restart_delay = 0
                game_state["status"] = "running"
                game_state["status_text"] = "Game running - auto restart"
                game_state["score"] = 0
                print("Agent mode: auto-restarting game")
        
        # Update game state
        if game_started and not game.game_over:
            game_state["status"] = "running"
            game_state["status_text"] = "Game running"
            
            if game_state["mode"] == "agent" and game_state["agent"]:
                try:
                    # Agent plays the game
                    state = game.get_state_for_agent()
                    action = game_state["agent"].act(state, explore=False)
                    game_state["last_action"] = action
                    _, _, _, info = game.step(action)
                    game_state["score"] = info["score"]
                except Exception as e:
                    print(f"Error during agent gameplay: {e}")
                    game_state["status_text"] = f"Agent error: {str(e)}"
                    game.game_over = True
            else:
                # Human plays the game
                _, _, _, info = game.step()
                game_state["score"] = info["score"]
        elif game.game_over:
            game_state["status"] = "game_over"
            game_state["status_text"] = "Game over"
        else:
            game_state["status"] = "waiting"
            game_state["status_text"] = "Waiting to start"
        
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
    return render_template('game_play.html', 
                           mode=game_state["mode"], 
                           model_path=game_state["model_path"] or "None")

@app.route('/get_game_state', methods=['GET'])
def get_game_state():
    """Return the current game state including the frame."""
    try:
        response = {
            "frame": game_state.get("frame", None),
            "score": game_state.get("score", 0),
            "status": game_state.get("status", "waiting"),
            "status_text": game_state.get("status_text", "Waiting to start"),
            "last_action": game_state.get("last_action", None),
            "success": True,
            "error": None
        }
        return jsonify(response)
    except Exception as e:
        # Log the error on the server side
        print(f"Error in get_game_state: {str(e)}")
        # Return a valid JSON response even in case of error
        return jsonify({
            "success": False,
            "error": str(e),
            "status": game_state.get("status", "error"),
            "status_text": f"Error: {str(e)}"
        })

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

@app.errorhandler(Exception)
def handle_error(e):
    """Handle any unhandled exceptions and return JSON response for API endpoints."""
    print(f"Global error handler caught: {str(e)}")
    import traceback
    traceback.print_exc()
    
    # Check if this is an API request (better to do this by path, but this is simpler)
    if request.path.startswith('/api/') or request.path == '/get_game_state' or request.path == '/get_frame':
        return jsonify({
            "success": False,
            "error": str(e),
            "status": "error",
            "status_text": f"Server error: {str(e)}"
        }), 500
    
    # For regular pages, still show an error page
    return f"<h1>Server Error</h1><p>{str(e)}</p>", 500

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
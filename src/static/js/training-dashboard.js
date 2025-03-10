/**
 * Snake Game Training Dashboard
 * Interactive monitoring and control of the snake game reinforcement learning process
 */

/* global Chart */

// Global variables
let speed = 1;
let paused = false;
let lastUpdateTime = null;
const pollingInterval = 100; // ms between updates
const isPolling = true;
let scoreChart;
let lastProcessedLogCount = 0; // Track how many logs we've already processed

/**
 * Initialize everything when the page is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
  // Initialize the chart
  initChart();

  // Add event listeners to buttons
  setupEventListeners();

  // Start polling for updates
  pollForUpdates();

  // Initial log
  logToConsole('Snake Game Training Dashboard v1.1 initialized');
  logToConsole('Connecting to training server...');
});

/**
 * Initialize the Chart.js visualization
 */
function initChart() {
  const ctx = document.getElementById('scoreChart').getContext('2d');
  scoreChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'Score',
        data: [],
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
        fill: false
      }, {
        label: 'Average Score',
        data: [],
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1,
        fill: false
      }, {
        label: 'Epsilon',
        data: [],
        borderColor: 'rgb(54, 162, 235)',
        tension: 0.1,
        fill: false,
        yAxisID: 'y1'
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Score'
          }
        },
        y1: {
          beginAtZero: true,
          max: 1,
          position: 'right',
          title: {
            display: true,
            text: 'Epsilon'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Episode'
          }
        }
      }
    }
  });
}

/**
 * Attach event listeners to buttons and other interactive elements
 */
function setupEventListeners() {
  // Pause/Resume button
  document.getElementById('pauseBtn').addEventListener('click', function() {
    paused = !paused;
    fetch('/api/control', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ command: paused ? 'pause' : 'resume' })
    });
    this.textContent = paused ? 'Resume' : 'Pause';
    logToConsole(paused ? 'Training paused' : 'Training resumed');
  });

  // Speed down button
  document.getElementById('speedDown').addEventListener('click', function() {
    if (speed > 0.25) {
      speed = Math.max(0.25, speed - 0.25);
      updateSpeed(speed);
    }
  });

  // Speed up button
  document.getElementById('speedUp').addEventListener('click', function() {
    if (speed < 4) {
      speed = Math.min(4, speed + 0.25);
      updateSpeed(speed);
    }
  });

  // Clear console button
  document.getElementById('clearConsole').addEventListener('click', function() {
    document.getElementById('console-content').innerHTML = '';
    logToConsole('Console cleared');
  });
}

/**
 * Update the speed display and send to server
 */
function updateSpeed(newSpeed) {
  fetch('/api/control', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ command: 'speed', value: newSpeed })
  });
  document.getElementById('speedDisplay').textContent = `Speed: ${newSpeed}x`;
  logToConsole(`Speed changed to ${newSpeed}x`);
}

/**
 * Start polling the server for updates
 */
function pollForUpdates() {
  if (!isPolling) return;

  fetch('/api/state')
    .then(response => response.json())
    .then(data => {
      lastUpdateTime = new Date();

      // Update connection status
      const connectionStatus = document.getElementById('connection-status');
      connectionStatus.className = 'connected';
      connectionStatus.textContent = 'Connected';

      // Update dashboard with the new data
      updateDashboard(data);
    })
    .catch(error => {
      const connectionStatus = document.getElementById('connection-status');
      connectionStatus.className = 'disconnected';
      connectionStatus.textContent = 'Connection Error';
      logToConsole(`Connection error: ${error.message}`);
    })
    .finally(() => {
      // Schedule next poll
      setTimeout(pollForUpdates, pollingInterval);
    });
}

/**
 * Monitor for lost updates
 */
setInterval(() => {
  if (lastUpdateTime) {
    const secondsSinceUpdate = (new Date() - lastUpdateTime) / 1000;
    if (secondsSinceUpdate > 10) {
      const connectionStatus = document.getElementById('connection-status');
      connectionStatus.className = 'disconnected';
      connectionStatus.textContent = 'Updates Stalled';
      logToConsole(`No updates for ${Math.floor(secondsSinceUpdate)} seconds`);
    }
  }
}, 5000);

/**
 * Process any new log messages
 */
function processLogMessages(messages) {
  if (!messages || messages.length === 0) return;

  const consoleContent = document.getElementById('console-content');
  const wasAtBottom = consoleContent.scrollHeight - consoleContent.clientHeight <= consoleContent.scrollTop + 5;

  // Get new messages since our last update
  const newMessages = messages.slice(lastProcessedLogCount);

  // Update our counter
  lastProcessedLogCount = messages.length;

  // Add new messages to the console
  for (const logMsg of newMessages) {
    const logElement = document.createElement('div');
    logElement.className = 'log-message';
    logElement.innerHTML = `<span class="timestamp">${logMsg.timestamp}</span> ${logMsg.message}`;
    consoleContent.appendChild(logElement);
  }

  // Auto-scroll if we were at the bottom before adding new messages
  if (wasAtBottom) {
    consoleContent.scrollTop = consoleContent.scrollHeight;
  }
}

/**
 * Update all dashboard elements with new data
 */
function updateDashboard(data) {
  // Update game display
  if (data.frame_base64) {
    document.getElementById('game-canvas').src = 'data:image/png;base64,' + data.frame_base64;
  }

  // Update statistics
  document.getElementById('episode').textContent = `${data.episode}/${data.total_episodes}`;
  document.getElementById('score').textContent = data.score;
  document.getElementById('avgScore').textContent = data.avg_score.toFixed(2);
  document.getElementById('epsilon').textContent = data.epsilon.toFixed(4);
  document.getElementById('timeouts').textContent = data.timeouts;
  document.getElementById('step').textContent = data.step;
  document.getElementById('lastUpdate').textContent = lastUpdateTime ? lastUpdateTime.toLocaleTimeString() : 'Never';

  // Update progress bar
  const progress = (data.episode / data.total_episodes) * 100;
  document.getElementById('episodeProgress').style.width = `${progress}%`;
  document.getElementById('episodeProgress').textContent = `${progress.toFixed(1)}%`;

  // Update chart
  if (data.episode > 0 && data.episode > scoreChart.data.labels.length) {
    scoreChart.data.labels.push(data.episode);
    scoreChart.data.datasets[0].data.push(data.score);
    scoreChart.data.datasets[1].data.push(data.avg_score);
    scoreChart.data.datasets[2].data.push(data.epsilon);
    scoreChart.update();
  }

  // Process any new log messages
  if (data.log_messages && data.log_messages.length > 0) {
    processLogMessages(data.log_messages);
  }
}

/**
 * Log a message to the console display
 */
function logToConsole(message) {
  const console = document.getElementById('console-content');
  const timestamp = new Date().toLocaleTimeString();
  console.innerHTML += `<div><span class="timestamp">${timestamp}</span> ${message}</div>`;
  console.scrollTop = console.scrollHeight;
}

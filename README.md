# Event Planning System

A Pub/Sub based event planning system that demonstrates the interaction between Event Hosts, Coordinators, and Guests using Redis as the message broker.

## Prerequisites

- Python 3.8+
- Redis Server

## Installation

1. Install Redis server if you haven't already:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start Redis server:
   ```bash
   redis-server
   ```

## Running the System

The system consists of three main components that need to be run in separate terminal windows:

1. Start the Coordinator:
   ```bash
   python coordinator.py
   ```

2. Start the Guests (in a new terminal):
   ```bash
   python guest.py
   ```

3. Start the Host (in a new terminal):
   ```bash
   python host.py
   ```

## How it Works

1. The Host creates an event invitation and publishes it to the Coordinator
2. The Coordinator receives the invitation and forwards it to all registered Guests
3. Each Guest receives the invitation, makes a decision (simulated), and sends a response
4. The Coordinator collects all responses and creates a summary
5. The summary is sent back to the Host, who displays the final guest list

## Configuration

The system uses environment variables for configuration. You can create a `.env` file with the following variables:

```
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Architecture

- `common.py`: Contains shared data models and utilities
- `host.py`: Implements the Event Host functionality
- `coordinator.py`: Implements the Coordinator service
- `guest.py`: Implements the Guest functionality

## Features

- Asynchronous communication using Redis Pub/Sub
- Type-safe message passing using Pydantic models
- Simulated guest decision making
- Real-time event summary generation
- Configurable through environment variables 
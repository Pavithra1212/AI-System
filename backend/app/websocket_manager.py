import json
import logging
from typing import List
from fastapi import WebSocket

logger = logging.getLogger(__name__)

MAX_CONNECTIONS = 100


class ConnectionManager:
    """Manages WebSocket connections for real-time admin notifications."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        if len(self.active_connections) >= MAX_CONNECTIONS:
            await websocket.close(code=1013, reason="Too many connections")
            return
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket connected. Total: %d", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("WebSocket disconnected. Total: %d", len(self.active_connections))

    async def broadcast(self, message: dict):
        """Send a JSON message to all connected admin clients."""
        disconnected = []
        # Copy list to avoid mutation during iteration
        connections = self.active_connections.copy()
        data = json.dumps(message)
        for connection in connections:
            try:
                await connection.send_text(data)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()

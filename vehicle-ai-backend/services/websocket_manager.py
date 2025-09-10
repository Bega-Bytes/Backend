import json
import logging
import asyncio
import time
from typing import List, Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("websocket-manager")


class ConnectionManager:
    """Manages WebSocket connections for real-time communication"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_info: Dict[WebSocket, Dict[str, Any]] = {}
        self._heartbeat_task: Optional[asyncio.Task] = None
        self.heartbeat_interval = 30000  # 30 seconds

        logger.info("WebSocket Connection Manager initialized")

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()
            self.active_connections.append(websocket)

            # Store connection info
            self.connection_info[websocket] = {
                "connected_at": time.time(),
                "client_host": websocket.client.host if websocket.client else "unknown",
                "last_ping": time.time(),
                "message_count": 0
            }

            logger.info(f"New WebSocket connection from {websocket.client.host if websocket.client else 'unknown'}")
            logger.info(f"Total active connections: {len(self.active_connections)}")

            # Start heartbeat if this is the first connection
            if len(self.active_connections) == 1:
                await self._start_heartbeat()

            # Send welcome message
            await self.send_personal_message(json.dumps({
                "type": "connection_established",
                "message": "Connected to Vehicle AI Backend",
                "timestamp": time.time(),
                "connection_id": id(websocket)
            }), websocket)

        except Exception as e:
            logger.error(f"Error connecting WebSocket: {e}")
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

            if websocket in self.connection_info:
                connection_duration = time.time() - self.connection_info[websocket]["connected_at"]
                message_count = self.connection_info[websocket]["message_count"]
                client_host = self.connection_info[websocket]["client_host"]

                logger.info(f"WebSocket disconnected from {client_host}")
                logger.info(f"Connection duration: {connection_duration:.1f}s, Messages: {message_count}")

                del self.connection_info[websocket]

            logger.info(f"Remaining active connections: {len(self.active_connections)}")

            # Stop heartbeat if no connections remain
            if len(self.active_connections) == 0:
                self._stop_heartbeat()

        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            if websocket in self.active_connections:
                await websocket.send_text(message)

                # Update message count
                if websocket in self.connection_info:
                    self.connection_info[websocket]["message_count"] += 1

                logger.debug(f"Sent personal message to {websocket.client.host if websocket.client else 'unknown'}")
            else:
                logger.warning("Attempted to send message to disconnected WebSocket")

        except WebSocketDisconnect:
            logger.info("WebSocket disconnected during message send")
            self.disconnect(websocket)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        """Broadcast a message to all connected WebSocket clients"""
        if not self.active_connections:
            logger.debug("No active connections for broadcast")
            return

        logger.info(f"Broadcasting message to {len(self.active_connections)} connections")

        # Create list of tasks for concurrent sending
        tasks = []
        disconnected_clients = []

        for connection in self.active_connections.copy():
            try:
                task = asyncio.create_task(connection.send_text(message))
                tasks.append((task, connection))
            except Exception as e:
                logger.error(
                    f"Error creating broadcast task for {connection.client.host if connection.client else 'unknown'}: {e}")
                disconnected_clients.append(connection)

        # Wait for all sends to complete
        for task, connection in tasks:
            try:
                await task
                # Update message count
                if connection in self.connection_info:
                    self.connection_info[connection]["message_count"] += 1
            except WebSocketDisconnect:
                logger.info(
                    f"WebSocket disconnected during broadcast: {connection.client.host if connection.client else 'unknown'}")
                disconnected_clients.append(connection)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection.client.host if connection.client else 'unknown'}: {e}")
                disconnected_clients.append(connection)

        # Clean up disconnected clients
        for connection in disconnected_clients:
            self.disconnect(connection)

        successful_sends = len(self.active_connections)
        logger.info(f"Broadcast completed: {successful_sends} successful, {len(disconnected_clients)} failed")

    async def broadcast_state_update(self, update_data: Dict[str, Any]):
        """Broadcast a vehicle state update to all clients"""
        message = {
            "type": "state_update",
            "data": update_data,
            "timestamp": time.time()
        }

        logger.info(
            f"Broadcasting state update: {update_data.get('system', 'unknown')} - {update_data.get('action', 'unknown')}")
        await self.broadcast(json.dumps(message))

    async def broadcast_command_result(self, command: str, result: Dict[str, Any], success: bool):
        """Broadcast command execution result to all clients"""
        message = {
            "type": "command_result",
            "data": {
                "command": command,
                "result": result,
                "success": success,
                "timestamp": time.time()
            }
        }

        logger.info(f"Broadcasting command result: {command} - {'Success' if success else 'Failed'}")
        await self.broadcast(json.dumps(message))

    async def send_error_to_client(self, websocket: WebSocket, error_message: str, error_code: str = "GENERAL_ERROR"):
        """Send an error message to a specific client"""
        error_data = {
            "type": "error",
            "data": {
                "code": error_code,
                "message": error_message,
                "timestamp": time.time()
            }
        }

        logger.warning(f"Sending error to client: {error_code} - {error_message}")
        await self.send_personal_message(json.dumps(error_data), websocket)

    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about active connections"""
        total_connections = len(self.active_connections)
        total_messages = sum(info["message_count"] for info in self.connection_info.values())

        connection_details = []
        for websocket, info in self.connection_info.items():
            connection_details.append({
                "client_host": info["client_host"],
                "connected_at": info["connected_at"],
                "connection_duration": time.time() - info["connected_at"],
                "message_count": info["message_count"],
                "last_ping": info["last_ping"]
            })

        return {
            "total_connections": total_connections,
            "total_messages_sent": total_messages,
            "connections": connection_details,
            "heartbeat_active": self._heartbeat_task is not None and not self._heartbeat_task.done()
        }

    async def ping_all_connections(self):
        """Send ping to all connections to check if they're alive"""
        if not self.active_connections:
            return

        ping_message = {
            "type": "ping",
            "timestamp": time.time()
        }

        logger.debug(f"Pinging {len(self.active_connections)} connections")

        disconnected_clients = []
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(json.dumps(ping_message))
                if connection in self.connection_info:
                    self.connection_info[connection]["last_ping"] = time.time()
            except Exception as e:
                logger.warning(f"Ping failed for {connection.client.host if connection.client else 'unknown'}: {e}")
                disconnected_clients.append(connection)

        # Clean up failed connections
        for connection in disconnected_clients:
            self.disconnect(connection)

    async def _start_heartbeat(self):
        """Start the heartbeat task to ping connections periodically"""
        if self._heartbeat_task is None or self._heartbeat_task.done():
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            logger.info("Started WebSocket heartbeat task")

    def _stop_heartbeat(self):
        """Stop the heartbeat task"""
        if self._heartbeat_task and not self._heartbeat_task.done():
            self._heartbeat_task.cancel()
            logger.info("Stopped WebSocket heartbeat task")

    async def _heartbeat_loop(self):
        """Heartbeat loop to maintain connections"""
        try:
            while True:
                await asyncio.sleep(30)  # Ping every 30 seconds
                if self.active_connections:  # Only ping if there are connections
                    await self.ping_all_connections()
                else:
                    break  # Exit loop if no connections
        except asyncio.CancelledError:
            logger.info("Heartbeat task cancelled")
        except Exception as e:
            logger.error(f"Error in heartbeat loop: {e}")

    async def shutdown(self):
        """Shutdown the connection manager"""
        logger.info("Shutting down WebSocket Connection Manager")

        # Cancel heartbeat task
        self._stop_heartbeat()
        if self._heartbeat_task:
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass

        # Close all connections
        disconnect_tasks = []
        for connection in self.active_connections.copy():
            try:
                disconnect_message = {
                    "type": "server_shutdown",
                    "message": "Server is shutting down",
                    "timestamp": time.time()
                }
                task = asyncio.create_task(connection.send_text(json.dumps(disconnect_message)))
                disconnect_tasks.append(task)
            except Exception as e:
                logger.error(f"Error sending shutdown message: {e}")

        # Wait for all disconnect messages to be sent
        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)

        # Clear all connections
        self.active_connections.clear()
        self.connection_info.clear()

        logger.info("WebSocket Connection Manager shutdown complete")
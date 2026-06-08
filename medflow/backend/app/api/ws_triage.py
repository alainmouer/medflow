"""WebSocket endpoint for real-time triage alerts (P1/P2)."""
from __future__ import annotations

import json

from fastapi import WebSocket, WebSocketDisconnect

from app.core.config import settings


class TriageConnectionManager:
    """Manage active WebSocket connections per tenant."""

    def __init__(self):
        # tenant_id -> list of WebSocket connections
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, tenant_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(tenant_id, []).append(websocket)

    def disconnect(self, tenant_id: str, websocket: WebSocket):
        connections = self.active_connections.get(tenant_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections:
            self.active_connections.pop(tenant_id, None)

    async def broadcast(self, tenant_id: str, message: dict):
        connections = self.active_connections.get(tenant_id, [])
        disconnected: list[WebSocket] = []
        for ws in connections:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(tenant_id, ws)


manager = TriageConnectionManager()


async def triage_ws_endpoint(websocket: WebSocket):
    """WebSocket handler for triage alerts."""
    # Expect a simple access_token in query params for lightweight auth
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return

    try:
        from jose import jwt as jose_jwt
        payload = jose_jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        tenant_id = payload.get("tenant_id")
        if not tenant_id:
            await websocket.close(code=4002)
            return
    except Exception:
        await websocket.close(code=4003)
        return

    await manager.connect(tenant_id, websocket)
    try:
        while True:
            # Keep connection alive, discard incoming client data
            data = await websocket.receive_text()
            # echo back ignored for heartbeat
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        manager.disconnect(tenant_id, websocket)
    except Exception:
        manager.disconnect(tenant_id, websocket)

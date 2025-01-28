from typing import Dict, List

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# ConnectionManager: WebSocket 연결 관리
class ConnectionManager:
    def __init__(self):
        # {WebSocket: username} 형태로 연결된 클라이언트 관리
        self.active_connections: Dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections[websocket] = username

    def disconnect(self, websocket: WebSocket):
        self.active_connections.pop(websocket, None)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# WebSocket 엔드포인트
@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    # 유저 연결 및 이름 등록
    await manager.connect(websocket, username)
    try:
        while True:
            # 메시지 수신
            data = await websocket.receive_text()
            print(f"Received from {username}: {data}")

            # 유저 이름을 포함한 메시지로 응답
            response = f"{username}: {data}"
            await manager.broadcast(response)
    except WebSocketDisconnect:
        # 유저 연결 해제
        manager.disconnect(websocket)
        print(f"Disconnected: {username}")
        await manager.broadcast(f"{username} has left the chat.")

# HTML 정적 파일 제공
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

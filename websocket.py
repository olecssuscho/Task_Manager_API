from typing import Dict
from fastapi import Depends, WebSocket,WebSocketDisconnect,APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth import decode_token
from depends import get_db
from schemas.dbmodels import ProjectMemberDB, UserDB

router = APIRouter()

class WebSocketManager():

    def __init__(self):
        self.active_connections : Dict[int,Dict[int, WebSocket]] = {}

    async def connect(self, websocket:WebSocket, project_id:int, user_id:int):
        if project_id not in self.active_connections:
            self.active_connections[project_id] = {}
        self.active_connections[project_id][user_id] = websocket

    async def disconnect(self, project_id:int, user_id:int):
        if project_id in self.active_connections and user_id in self.active_connections[project_id]:
            del self.active_connections[project_id][user_id]
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]

    async def broadcast(self, project_id:int, message:str):
        users = self.active_connections.get(project_id,{})
        for user_id,websocket in list(users.items()):
            try:
                await websocket.send_text(message)
            except Exception:
                await self.disconnect(project_id, user_id)
                
manager = WebSocketManager()

@router.websocket("/ws/websocket/{token}/{project_id}")
async def websocket_endpoint(websocket: WebSocket, token: str,project_id: int, db: AsyncSession = Depends(get_db)):
    await websocket.accept()

    payload = decode_token(token)
    if payload is None:
        await websocket.close(1008)
        return
    
    stmt = await db.execute(select(UserDB).filter(UserDB.email == payload["email"]))
    user = stmt.scalar_one_or_none()
    if not user:
        await websocket.close(1008)
        return

    stmt = await db.execute(select(ProjectMemberDB).filter(ProjectMemberDB.user_id == user.id,ProjectMemberDB.project_id == project_id))
    project = stmt.scalar_one_or_none()
    if not project:
        await websocket.close(1008)
        return

    await manager.connect(websocket,project_id,user.id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(project_id,user.id)
        

            


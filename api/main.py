# api/main.py
# FastAPI app: saves detections to MongoDB Atlas, upserts aggregated intersection state,
# keeps a state history, and broadcasts live state to WebSocket clients.
import os
import time
import asyncio
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise RuntimeError("Please set MONGODB_URI in environment or .env file (see .env.template)")

client = AsyncIOMotorClient(MONGODB_URI)
# default database name is parsed from the URI; if not present, use 'atsc_db'
db = client.get_database()
if db is None:
    db = client["atsc_db"]
detections_coll = db["detections"]
states_coll = db["states"]
states_history_coll = db["states_history"]

app = FastAPI(title="ATSC API (MongoDB Atlas)")

# in-memory state (fallback). We will also persist state to Atlas.
STATE = {"intersection_1": {"queues": [0,0,0,0], "phase": 0, "last_update": 0}}

class Vehicle(BaseModel):
    track_id: Optional[int] = None
    cls: str
    conf: float
    bbox: List[int]

class IngestBody(BaseModel):
    camera_id: str
    ts: float
    vehicles: List[Vehicle]

# Simple WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        living = []
        for conn in list(self.active_connections):
            try:
                await conn.send_json(message)
                living.append(conn)
            except Exception:
                # drop broken connections
                pass
        self.active_connections = living

manager = ConnectionManager()

@app.post("/ingest")
async def ingest(body: IngestBody):
    # store raw detection into Atlas
    doc = {
        "camera_id": body.camera_id,
        "ts": body.ts,
        "vehicles": [v.dict() for v in body.vehicles],
        "received_at": time.time()
    }
    await detections_coll.insert_one(doc)

    # simple aggregation: put vehicle count into lane 0 (demo)
    cnt = len(body.vehicles)
    STATE["intersection_1"]["queues"][0] = cnt
    STATE["intersection_1"]["last_update"] = time.time()

    # prepare state document
    state_doc = {
        "intersection_id": "intersection_1",
        "queues": STATE["intersection_1"]["queues"],
        "phase": STATE["intersection_1"]["phase"],
        "last_update": STATE["intersection_1"]["last_update"]
    }
    # upsert current state
    await states_coll.update_one(
        {"intersection_id": state_doc["intersection_id"]},
        {"$set": state_doc},
        upsert=True
    )
    # append to history for analytics
    await states_history_coll.insert_one({"intersection_id": state_doc["intersection_id"], "state": state_doc, "ts": time.time()})

    # broadcast to connected websockets
    try:
        await manager.broadcast(state_doc)
    except Exception:
        pass

    return {"status": "ok", "inserted": True, "count": cnt}

@app.get("/state/{intersection_id}")
async def get_state(intersection_id: str):
    # try DB first
    doc = await states_coll.find_one({"intersection_id": intersection_id})
    if doc:
        # remove _id if present
        doc.pop("_id", None)
        return doc
    # fallback
    return STATE.get(intersection_id, {"queues": [0,0,0,0], "phase": 0})

@app.get("/recent")
async def recent(limit: int = 10):
    # return recent detections from Atlas
    cursor = detections_coll.find().sort("received_at", -1).limit(limit)
    docs = []
    async for d in cursor:
        d["_id"] = str(d["_id"])
        docs.append(d)
    return {"count": len(docs), "docs": docs}

@app.websocket("/ws/{intersection_id}")
async def websocket_endpoint(websocket: WebSocket, intersection_id: str):
    await manager.connect(websocket)
    try:
        while True:
            # send current state periodically as a fallback
            st = STATE.get(intersection_id, {"queues": [0,0,0,0], "phase": 0})
            await websocket.send_json(st)
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

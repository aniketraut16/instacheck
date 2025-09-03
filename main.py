from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.flow import check_authenticity
from modules.wed_data_extractor.pipeline import get_wed_data
import json
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000", "https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE...
    allow_headers=["*"],  # Authorization, Content-Type...
)


@app.websocket("/api/checkAuthenticityWS")
async def check_authenticity_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        url = data
        if not url:
            await websocket.send_text(json.dumps({"step": "error", "message": "URL is required"}))
            await websocket.close()
            return

        await check_authenticity(websocket, url)
        
    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except json.JSONDecodeError:
        await websocket.send_text(json.dumps({"step": "error", "message": "Invalid JSON format"}))
    except Exception as e:
        await websocket.send_text(json.dumps({"step": "error", "message": f"An error occurred: {str(e)}"}))
    finally:
        try:
            await websocket.close()
        except:
            pass
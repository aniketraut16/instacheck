from fastapi import FastAPI
from app.flow import check_authenticity

app = FastAPI()

@app.post("/process")
async def check_authenticity_endpoint(request_data: dict):
    url = request_data.get("url")
    log = request_data.get("log", False)
    return await check_authenticity(url, log)
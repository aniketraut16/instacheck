from fastapi import FastAPI
from app.flow import check_authenticity
from modules.wed_data_extractor.pipeline import get_wed_data

app = FastAPI()

@app.post("/get-wed-data")
async def process_endpoint(request_data: dict):
    query = request_data.get("query")
    return await get_wed_data(query)

@app.post("/process")
async def check_authenticity_endpoint(request_data: dict):
    url = request_data.get("url")
    return await check_authenticity(url)
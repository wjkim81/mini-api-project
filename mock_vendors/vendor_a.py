import random
import asyncio

from fastapi import FastAPI, HTTPException

from app.schemas import VendorRequest, VendorResponse

app = FastAPI(title="Mock Vendor A")


@app.post("/infer", response_model=VendorResponse)
async def infer(request: VendorRequest) -> VendorResponse:
    await asyncio.sleep(0.2)  # fast vendor

    roll = random.random()

    if roll < 0.4:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    if roll < 0.8:
        raise HTTPException(status_code=500, detail="Internal server error")

    return VendorResponse(
        vendor="vendor_a",
        result=f"processed by vendor_a: {request.input_text}",
    )
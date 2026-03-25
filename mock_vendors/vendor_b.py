import random
import asyncio

from fastapi import FastAPI

from app.schemas import VendorRequest, VendorResponse

app = FastAPI(title="Mock Vendor B")


@app.post("/infer", response_model=VendorResponse)
async def infer(request: VendorRequest) -> VendorResponse:
    roll = random.random()

    if roll < 0.15:
        await asyncio.sleep(3.0)  # simulate timeout
    else:
        await asyncio.sleep(0.8)

    return VendorResponse(
        vendor="vendor_b",
        result=f"processed by vendor_b: {request.input_text}",
    )
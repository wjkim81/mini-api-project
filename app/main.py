import uuid

from fastapi import FastAPI, HTTPException

from .schemas import ProcessRequest, ProcessResponse, StoredResponse
from .store import IdempotencyStore
from .vendor_client import VendorClientError, process_with_fallback

app = FastAPI(title="Resilient API Gateway")

store = IdempotencyStore()


@app.post("/process", response_model=ProcessResponse)
async def process(request: ProcessRequest) -> ProcessResponse:
    request_id = str(uuid.uuid4())

    cached_item = store.get(request.idempotency_key)
    if cached_item is not None:
        return ProcessResponse(
            request_id=request_id,
            idempotency_key=cached_item.idempotency_key,
            vendor_used=cached_item.vendor_used,
            result=cached_item.result,
            cached=True,
        )

    try:
        vendor_response = await process_with_fallback(request.input_text)
    except VendorClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    stored_item = StoredResponse(
        idempotency_key=request.idempotency_key,
        vendor_used=vendor_response.vendor,
        result=vendor_response.result,
    )
    store.save(stored_item)

    return ProcessResponse(
        request_id=request_id,
        idempotency_key=request.idempotency_key,
        vendor_used=vendor_response.vendor,
        result=vendor_response.result,
        cached=False,
    )
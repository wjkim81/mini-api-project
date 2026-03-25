from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):
    input_text: str = Field(..., min_length=1)
    idempotency_key: str = Field(..., min_length=1)


class ProcessResponse(BaseModel):
    request_id: str
    idempotency_key: str
    vendor_used: str
    result: str
    cached: bool


class StoredResponse(BaseModel):
    idempotency_key: str
    vendor_used: str
    result: str


class VendorRequest(BaseModel):
    input_text: str = Field(..., min_length=1)


class VendorResponse(BaseModel):
    vendor: str
    result: str
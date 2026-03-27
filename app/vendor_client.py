import asyncio

import httpx

from .schemas import VendorRequest, VendorResponse

VENDOR_A_URL = "http://127.0.0.1:9001/infer"
VENDOR_B_URL = "http://127.0.0.1:9002/infer"


class VendorClientError(Exception):
    """Base exception for vendor client errors."""


class VendorHTTPError(VendorClientError):
    def __init__(self, vendor_name: str, status_code: int, detail: str) -> None:
        self.vendor_name = vendor_name
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"{vendor_name} returned {status_code}: {detail}")


class VendorResponseFormatError(VendorClientError):
    def __init__(self, vendor_name: str, detail: str) -> None:
        self.vendor_name = vendor_name
        self.detail = detail
        super().__init__(f"{vendor_name} returned invalid response: {detail}")


class VendorTimeoutError(VendorClientError):
    def __init__(self, vendor_name: str) -> None:
        self.vendor_name = vendor_name
        super().__init__(f"{vendor_name} request timed out")

class VendorConnectionError(VendorClientError):
    def __init__(self, vendor_name: str, detail: str) -> None:
        self.vendor_name = vendor_name
        self.detail = detail
        super().__init__(f"{vendor_name} connection failed: {detail}")


async def call_vendor_once(
    vendor_name: str,
    vendor_url: str,
    input_text: str,
) -> VendorResponse:
    payload = VendorRequest(input_text=input_text)

    timeout = httpx.Timeout(1.0, connect=0.5)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(vendor_url, json=payload.model_dump())

        if response.status_code != 200:
            raise VendorHTTPError(
                vendor_name=vendor_name,
                status_code=response.status_code,
                detail=response.text,
            )

        try:
            return VendorResponse.model_validate(response.json())
        except Exception as exc:
            raise VendorResponseFormatError(vendor_name, str(exc)) from exc

    except httpx.TimeoutException as exc:
        raise VendorTimeoutError(vendor_name) from exc
    except httpx.ConnectError as exc:
        raise VendorConnectionError(vendor_name, str(exc)) from exc
    except httpx.TimeoutException as exc:
        raise VendorTimeoutError(vendor_name) from exc


def is_retryable_error(error: Exception) -> bool:
    if isinstance(error, VendorTimeoutError):
        return True

    if isinstance(error, VendorHTTPError):
        if error.status_code == 429:
            return True
        if 500 <= error.status_code < 600:
            return True
        return False

    if isinstance(error, VendorConnectionError):
        return True

    if isinstance(error, VendorResponseFormatError):
        return False

    return False


async def call_vendor_with_retry(
    vendor_name: str,
    vendor_url: str,
    input_text: str,
    max_retries: int = 3,
) -> VendorResponse:
    last_error: VendorClientError | None = None

    for attempt in range(max_retries + 1):
        try:
            print(f"[retry] calling {vendor_name}, attempt={attempt + 1}")
            return await call_vendor_once(
                vendor_name=vendor_name,
                vendor_url=vendor_url,
                input_text=input_text,
            )

        except VendorClientError as error:
            print(f"[retry] {vendor_name} failed on attempt {attempt + 1}: {error}")
            last_error = error

            if not is_retryable_error(error):
                raise

            if attempt == max_retries:
                break

            print(f"[retry] sleeping {sleep_time:.1f}s before retrying {vendor_name}")
            sleep_time = 0.5 * (2 ** attempt)
            await asyncio.sleep(sleep_time)

    if last_error:
        raise last_error

    raise VendorClientError("Unknown error in retry logic")


async def process_with_fallback(input_text: str) -> VendorResponse:
    try:
        return await call_vendor_with_retry(
            vendor_name="vendor_a",
            vendor_url=VENDOR_A_URL,
            input_text=input_text,
        )
    except VendorClientError as vendor_a_error:
        print(f"[fallback] vendor_a failed: {vendor_a_error}")

    return await call_vendor_with_retry(
        vendor_name="vendor_b",
        vendor_url=VENDOR_B_URL,
        input_text=input_text,
    )
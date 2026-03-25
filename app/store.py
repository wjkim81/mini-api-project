from typing import Optional

from .schemas import StoredResponse


class IdempotencyStore:
    def __init__(self) -> None:
        self._store: dict[str, StoredResponse] = {}

    def get(self, idempotency_key: str) -> Optional[StoredResponse]:
        return self._store.get(idempotency_key)

    def save(self, item: StoredResponse) -> None:
        self._store[item.idempotency_key] = item
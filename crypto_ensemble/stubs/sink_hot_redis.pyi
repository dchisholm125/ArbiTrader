from typing import Dict, List, Protocol

class Publisher(Protocol):
    async def send(self, topic: str, data: bytes) -> None: ...

class RedisPublisher(Publisher):
    def __init__(self, url: str, stream: str) -> None: ...

class InMemoryPublisher(Publisher):
    def __init__(self) -> None: ...
    messages: Dict[str, List[bytes]]

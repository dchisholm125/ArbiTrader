from typing import Awaitable, Callable, Dict

class LatencyProbe:
    def __init__(self, clock: Callable[[], float] | None = ...) -> None: ...
    async def measure(
        self, venue: str, rpc: Callable[[], Awaitable[None]]
    ) -> Dict[str, float]: ...

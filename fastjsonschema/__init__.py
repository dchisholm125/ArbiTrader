from typing import Any, Callable, Dict


def compile(schema: Dict[str, Any]) -> Callable[[Any], Any]:
    def validate(data: Any) -> Any:
        return data

    return validate

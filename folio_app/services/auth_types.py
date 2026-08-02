from dataclasses import dataclass


@dataclass(frozen=True)
class AuthResult:
    ok: bool
    message: str


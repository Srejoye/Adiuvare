class IdentityStore:
    def __init__(self) -> None:
        self._blocked: set[str] = set()
        self._seen: dict[str, int] = {}

    def is_blocked(self, identity: str) -> bool:
        return identity in self._blocked

    def block(self, identity: str) -> None:
        self._blocked.add(identity)

    def unblock(self, identity: str) -> None:
        self._blocked.discard(identity)

    def bump(self, identity: str) -> int:
        now = self._seen.get(identity, 0) + 1
        self._seen[identity] = now
        return now


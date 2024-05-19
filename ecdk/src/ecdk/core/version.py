class Version:
    __slots__ = ('major', 'minor', 'patch')

    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor
        self.patch = patch

    @classmethod
    def from_str(cls, version_str: str):
        parts = version_str.split('.')
        assert len(parts) == 3, f"Expected exactly 3 parts in version string spec, got {len(parts)}"
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        return cls(major, minor, patch)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        return str(self)



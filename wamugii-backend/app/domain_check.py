"""
Check live domain availability from the server, to confirm the registries
answer before you rely on the search page:

    docker exec wamugii-backend python -m app.domain_check kigalishop.rw google.com
"""

import asyncio
import sys

from app.services import domain_lookup


async def main(names: list[str]) -> int:
    pairs = []
    for raw in names:
        name, ext = domain_lookup.parse_query(raw, [".co.rw", ".org.rw", ".ac.rw"])
        ext = ext or ".rw"
        pairs.append((name + ext, ext))
    results = await domain_lookup.check_many(pairs)
    for r in results:
        extra = f"expires {r.expires_at}" if r.expires_at else (r.reason or "")
        print(f"{r.domain:32s} {r.status.upper():10s} {r.registrar or ''} {extra}".rstrip())
    return 0 if all(r.status != "unknown" for r in results) else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main(sys.argv[1:] or ["ricta.org.rw", "wamugii-test-123456.rw", "google.com"])))

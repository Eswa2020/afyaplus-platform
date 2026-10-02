"""MCP health gate (Route A): a stdio client handshake, not an HTTP port.

Launches the server, initialises a session, lists tools, reads version://current,
and asserts the required tools exist and the major version is as expected.
"""
import asyncio
import sys

SERVER_FILE = "logistics_mcp_versioned.py"
EXPECTED_TOOLS = {"check_stock"}
EXPECTED_VERSION_PREFIX = "1."
TIMEOUT_S = 30


async def handshake() -> int:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(command=sys.executable, args=[SERVER_FILE])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = {t.name for t in (await session.list_tools()).tools}
            result = await session.read_resource("version://current")
            version = result.contents[0].text if result.contents else ""
            print("tools", sorted(tools), "version", version)

            ok = True
            missing = EXPECTED_TOOLS - tools
            if missing:
                print("missing tools", missing)
                ok = False
            if not version.startswith(EXPECTED_VERSION_PREFIX):
                print(f"unexpected version {version!r}, expected {EXPECTED_VERSION_PREFIX}x")
                ok = False
            return 0 if ok else 1


def main() -> int:
    try:
        return asyncio.run(asyncio.wait_for(handshake(), TIMEOUT_S))
    except Exception as exc:  # noqa: BLE001 - any failure to handshake means unhealthy
        print("MCP HEALTH FAILED:", type(exc).__name__, exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
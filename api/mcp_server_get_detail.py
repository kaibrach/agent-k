from helpers.api import ApiHandler, Request, Response
from typing import Any

from helpers.mcp_handler import MCPConfig


class McpServerGetDetail(ApiHandler):
    async def process(self, input: dict[Any, Any], request: Request) -> dict[Any, Any] | Response:
        server_name = input.get("server_name")
        if not server_name:
            return {"success": False, "error": "Missing server_name"}

        detail = MCPConfig.get_instance().get_server_detail(server_name)
        if not detail:
            return {"success": False, "error": f"MCP server '{server_name}' was not found or has no detail available"}

        return {"success": True, "detail": detail}

from helpers.api import ApiHandler, Request, Response

from typing import Any

from helpers.mcp_handler import MCPConfig
from helpers.settings import set_settings_delta


class McpServersApply(ApiHandler):
    async def process(self, input: dict[Any, Any], request: Request) -> dict[Any, Any] | Response:
        mcp_servers = input["mcp_servers"]
        try:
            set_settings_delta({"mcp_servers": mcp_servers}, apply=False)
            MCPConfig.update(mcp_servers)
            status = MCPConfig.get_instance().get_servers_status()
            return {"success": True, "status": status}

        except Exception as e:
            return {"success": False, "error": str(e)}

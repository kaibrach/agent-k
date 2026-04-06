import json
from typing import Any

from helpers.api import ApiHandler, Request, Response
from helpers import dirty_json, settings
from helpers.mcp_handler import MCPConfig, normalize_name


def _normalize_config_object(parsed: Any) -> dict[str, Any]:
    if isinstance(parsed, dict) and isinstance(parsed.get("mcpServers"), dict):
        return parsed

    if isinstance(parsed, list):
        mcp_servers: dict[str, Any] = {}
        for item in parsed:
            if not isinstance(item, dict):
                continue
            name = item.get("name") or f"server-{len(mcp_servers) + 1}"
            clone = dict(item)
            clone.pop("name", None)
            mcp_servers[name] = clone
        return {"mcpServers": mcp_servers}

    if isinstance(parsed, dict):
        return {"mcpServers": parsed.get("mcpServers", {}) or {}}

    return {"mcpServers": {}}


class McpServerSetTools(ApiHandler):
    async def process(self, input: dict[Any, Any], request: Request) -> dict[Any, Any] | Response:
        server_name = str(input.get("server_name") or "").strip()
        disabled_tools = input.get("disabled_tools") or []

        if not server_name:
            return {"success": False, "error": "Missing server_name"}
        if not isinstance(disabled_tools, list):
            return {"success": False, "error": "disabled_tools must be a list"}

        current_settings = settings.get_settings()
        parsed = dirty_json.try_parse(current_settings.get("mcp_servers", "{}"))
        config_object = _normalize_config_object(parsed)
        mcp_servers = config_object.setdefault("mcpServers", {})
        normalized_name = normalize_name(server_name)

        target_key = None
        for key in mcp_servers.keys():
            if key == server_name or normalize_name(key) == normalized_name:
                target_key = key
                break

        if target_key is None:
            return {"success": False, "error": f"MCP server '{server_name}' not found in settings"}

        server_config = mcp_servers.get(target_key)
        if not isinstance(server_config, dict):
            return {"success": False, "error": f"MCP server '{server_name}' has invalid configuration"}

        sanitized_tools = sorted({str(name) for name in disabled_tools if str(name).strip()})
        if sanitized_tools:
            server_config["disabled_tools"] = sanitized_tools
        else:
            server_config.pop("disabled_tools", None)

        config_json = json.dumps(config_object, indent=2)
        settings.set_settings_delta({"mcp_servers": config_json}, apply=False)
        MCPConfig.get_instance().set_server_disabled_tools(target_key, sanitized_tools)

        return {
            "success": True,
            "mcp_servers": config_json,
            "status": MCPConfig.get_instance().get_servers_status(),
            "detail": MCPConfig.get_instance().get_server_detail(normalized_name),
        }
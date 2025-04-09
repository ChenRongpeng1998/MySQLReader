# MySQLReader
This is a MCP server about read data from mysql databsase . 
# Install
## step 0:install uv to manage your python

```bash
pip install uv
```
## step 1:clone the repository
The cloning path for this article is `D:\\Project`
## step 2:install necessary dependencies
```bash
cd MySQLReader
uv sync
.venv\Scripts\activate
```

# Run MCP Server
```bash
uv run mysql_reader.py
```
# Usage with Claude Desktop
uv
```
# Add the server to your claude_desktop_config.json
{
    "mcpServers": {
        "mysql_reader": {
            "command": "uv",
            "args": [
                "--directory",
                "Path\to\your\MySQLReader",
                "run",
                "mysql_reader.py",
                "host",
                "username",
                "password",
                "database"
            ]
        }
    }
}
```
# Tool
The server just offers querry tool `read_query`,and the tool is not described in the code
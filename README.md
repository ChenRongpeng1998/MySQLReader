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
                "mysql_reader.py"
            ]
        }
    }
}
```
# How to connect your mysql database
Before running the service,modify mysql_reader.py:
```python
conn = mysql.connector.connect(
host="localhost", # Modify to your own host
user="root", #Modify to your own user
password="123456", # Modify to your own password
database="mysql" , # Modify to your own database
)
```
# Tool
The server just offers querry tool `read_query`,and the tool is not described in the code
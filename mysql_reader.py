import mysql.connector
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("MysqlReader")

# 连接到 MySQL 数据库
conn = mysql.connector.connect(
    host="localhost",          # 数据库主机地址
    user="root",      # 数据库用户名
    password="123456",  # 数据库密码
    database="mysql" ,  # 要连接的数据库名称
)

@mcp.tool()
def read_query(sql_query_statement:str):
    if conn.is_connected():
        # 创建游标对象
        cursor = conn.cursor(dictionary=True)
        # 执行 SQL 查询
        query = sql_query_statement  # 替换为你的表名
        cursor.execute(query)

        # 获取查询结果
        results = cursor.fetchall()  # 获取所有行
        cursor.close()
        return results
    else:
        return "数据库已关闭"



if __name__ == "__main__":
    print("Starting MCP server...")
    # Initialize and run the server
    mcp.run(transport='stdio')
    print("Over MCP server...")
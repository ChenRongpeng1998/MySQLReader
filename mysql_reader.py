import mysql.connector
from mcp.server.fastmcp import FastMCP
import argparse
# Create an MCP server
mcp = FastMCP("MysqlReader")

# 连接到 MySQL 数据库
def connect_to_mysql(host, user, password, database):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        if conn.is_connected():
            print(f"Connected to MySQL database at {host}")
            return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None
parser = argparse.ArgumentParser(description="mysql database host address, username, password, database")
parser.add_argument("host", type=str, help="mysql database host address")
parser.add_argument("user", type=str, help="mysql database username")
parser.add_argument("pwd", type=str, help="mysql database password")
parser.add_argument("db", type=str, help="mysql database name")
args = parser.parse_args()
# 使用命令行参数连接到 MySQL 数据库
conn = connect_to_mysql(args.host, args.user, args.pwd, args.db)
@mcp.tool(description="This is a tool used to read data from MySQL databases. Through SQL queries, data can be retrieved from a specified table.Suitable for scenarios where data needs to be read from MySQL databases, such as querying records and statistical information in tables.")
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
        return "database closed"

if __name__ == "__main__":
    mcp.run(transport='stdio')



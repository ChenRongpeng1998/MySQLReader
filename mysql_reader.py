import pymysql
from mcp.server.fastmcp import FastMCP
import argparse
import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

load_dotenv()
# Create an MCP server
mcp = FastMCP("MysqlReader")

def is_connected(connection: pymysql.connections.Connection) -> bool:
    if connection is not None:
        try:
            connection.ping(reconnect=True)
            return True
        except pymysql.err.OperationalError:
            return False
    return False

# 连接到 MySQL 数据库
def connect_to_mysql(host, user, _password, database):
    try:
        _conn = pymysql.connect(
            host=host,
            user=user,
            password=_password,
            database=database,
        )
        if is_connected(_conn):
            print(f"Connected to MySQL database at {host}")
            return _conn
    except pymysql.err as e:
        print(f"Error connecting to MySQL database: {e}")
        return None
def parse_arguments():
    parser = argparse.ArgumentParser(description="连接数据库所需要的一些参数")
    parser.add_argument("host", type=str, help="mysql database host address")
    parser.add_argument("db", type=str, help="想要连接的数据库名")
    parser.add_argument(
        "--authentication-method",
        choices=["ev", "file","efile"],
        required=False,
        default="ev",
        help="认证方式：ev(环境变量), file(显式文件)或efile(加密文件)"
    )
    parser.add_argument(
        "--file-path",
        help="当认证方式为 file 或 efile时，需要提供文件路径"
    )
    parser.add_argument(
        "--evname-user",
        type=str,
        default="DB_USERNAME",
        help="存储数据库用户名的环境变量名，注意是环境变量名")
    parser.add_argument(
        "--evname-pwd",
        type=str,
        default="DB_PASSWORD",
        help="存储数据库密码的环境变量名，注意是环境变量名")
    parser.add_argument(
        "--private_key_file_name",
        type=str,
        help="私钥文件名"
    )
    return parser.parse_args()

def get_credentials_from_env(user_v_name,pwd_v_name):
    username = os.environ.get(user_v_name)
    password = os.environ.get(pwd_v_name)
    if not username or not password:
        raise Exception("错误：环境变量中未找到 USERNAME 或 PASSWORD")
    return username, password

def get_credentials_from_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError("错误：文件 {file_path} 不存在")
    try:
        with open(file_path, "r") as f:
            lines = f.readlines()
            if len(lines) < 2:
                raise Exception("错误：文件格式不正确，至少需要两行（用户名和密码）")
            _username,_password = None,None
            for line in lines:
                if line.lower().startswith("username="):
                    _username = line.split("=")[1].strip()
                elif line.lower().startswith("password="):
                    _password = line.split("=")[1].strip()
            if not _username or not _password:
                raise Exception("错误：未能从文件中读取到用户名或密码")
            return _username, _password
    except Exception as e:
        raise

def load_private_key(file_path:str):
    if file_path.endswith(".pem") and os.path.exists(file_path):
        with open(file_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )
        return private_key
    return None

def load_encrypted_file(file_path:str):
    if file_path.endswith(".enc") and os.path.exists(file_path):
        with open(file_path, "rb") as encrypted_file:
            encrypted_data = encrypted_file.read()
        return encrypted_data

def get_credentials_from_efile(file_path,private_key_file_name):
    if not os.path.exists(file_path):
        raise FileNotFoundError("错误：文件 {file_path} 不存在")
    try:
        private_key = load_private_key(private_key_file_name)
        encrypted_data = load_encrypted_file(file_path)
        # 解密用户名和密码
        data = private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode()
        _username, _password = data.split("pwd:")
        return _username.strip(), _password.strip()
    except Exception as e:
        raise

args = parse_arguments()
username, password = None, None
if args.authentication_method == "ev":
    username, password = get_credentials_from_env(args.evname_user, args.evname_pwd)
elif args.authentication_method == "file":
    if not args.file_path:
        raise Exception("当--authentication-method为file或efile时必须传入文件路径--file-path")
    username, password = get_credentials_from_file(args.file_path)
elif args.authentication_method == "efile":
    if not args.file_path:
        raise Exception("当--authentication-method为file或efile时必须传入文件路径--file-path")
    if not args.private_key_file_name:
        raise Exception("当--authentication-method为efile时必须传入密钥文件路径--private_key_file_name")
    username, password = get_credentials_from_efile(args.file_path,args.private_key_file_name)
if not username or not password:
    raise ValueError("错误：未能读取到用户名或密码。")
try:
    # 使用命令行参数连接到 MySQL 数据库
    conn = connect_to_mysql(args.host, username, password, args.db)
except Exception:
    raise Exception("mysql database connection failed")
@mcp.tool(description="This is a tool used to read data from MySQL databases. Through SQL queries, data can be retrieved from a specified table.Suitable for scenarios where data needs to be read from MySQL databases, such as querying records and statistical information in tables.")
def read_query(sql_query_statement:str):
    if conn is not None and is_connected(conn):
            # 创建游标对象
            cursor = conn.cursor()
            # 执行 SQL 查询
            query = sql_query_statement  # 替换为你的表名
            cursor.execute(query)
            # 获取查询结果
            results = cursor.fetchall()  # 获取所有行
            cursor.close()
            return str(results)
    else:
        return "database closed"

@mcp.tool(description="Check if the database is available, return true or false")
def check_db_available():
    if conn is not None and is_connected(conn):
        return True
    return False

if __name__ == "__main__":
    mcp.run(transport='stdio')

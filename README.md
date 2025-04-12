# MySQLReader
这是一个用于读取MySQL数据库的MCP服务，基于安全性考量该MCP服务仅提供对于数据库的查询操作，增删改功能暂不支持。本服务的数据库功能均基于pymysql库实现，关于认证方式，本服务支持将数据库用户名密码存储至环境变量(ev)、.txt文件(file)和使用RSA算法加密的.enc文件(efile)三种方式供服务使用。
# 安装
## step 0:安装uv以管理Python

```bash
pip install uv
```
## step 1:克隆仓库至本地
本文克隆路径为 `D:\\Project`
## step 2:安装依赖
```bash
cd MySQLReader # 进入项目
uv sync # 同步环境
.venv\Scripts\activate # 激活虚拟环境
```
# 用法
mysql.py脚本用法如下：
```
usage: mysql_reader.py [-h] [--authentication-method {ev,file,efile}]
                       [--file-path FILE_PATH] [--evname-user EVNAME_USER]
                       [--evname-pwd EVNAME_PWD]
                       [--private_key_file_name PRIVATE_KEY_FILE_NAME]
                       host db
 ```
- host，必要参数，此参数为数据库地址，如:localhost
- db，必要参数，此参数为数据库名，如:mysql
- --authentication-method为认证方式，其值只能从ev、file和efile中选取。
- --evname-user为用户名存储的环境变量名，当认证方式为ev时系统从--evname-user指示的环境变量中
取用户名。
- --evname-pwd为密码存储的环境变量名，当认证方式为ev时系统从--evname-pwd指示的环境变量中
取密码。
- --file-path为文件路径，当认证方式为file或efile时，此参数指示 用户名和密码存储的文件位置。
- --private_key_file_name为密钥路径，当认证方式为efile时，系统从此参数指示的路径读取密钥。

## 在Claude Desktop上的用法
添加本服务到你的claude_desktop_config.json文件中
```
{
    "mcpServers": {
        "mysql_reader": {
            "command": "uv",
            "args": [
                "--directory",
                "Path\to\your\MySQLReader",
                "run",
                "mysql_reader.py",
                "your_database_host",
                "your_database",
                "--authentication-method",
                "ev" # 这是默认值可不填
            ]
        }
    }
}
```
## 认证方法 --authentication-method的说明
本服务支持如下三种认证方式：
- ev:将用户名和密码存储到环境变量中供服务使用。
- file:将用户名和密码显式的存储到某一txt文件中供服务使用。
- efile:将用户名和密码加密存储到某一.enc文件中供服务使用。
下面将详细介绍三种认证方式下claude_desktop_config.json的写法。
### 1.环境变量ev
本方法为`--authentication-method`的默认值，此时系统会从`--evname-user`和`--evname-pwd`指示的环境变量中读取用户名和密码，`--evname-user`和`--evname-pwd`的默认值分别为：DB_USERNAME和DB_PASSWORD。此方法下，claude_desktop_config.json示例如下：
```
{
    "mcpServers": {
        "mysql_reader": {
            "command": "uv",
            "args": [
                "--directory",
                "Path\to\your\MySQLReader",
                "run",
                "mysql_reader.py",
                "your_database_host",
                "your_database",
                "--authentication-method",
                "ev" # 这是默认值可不填,
                "--evname-user",
                "your_username_environment_variable",
                "--evname-pwd",
                "your_password_environment_variable",
                
            ]
        }
    }
}
```
### 2.显式文件file
当`--authentication-method`传入file时，系统会从`--file-path`指示的文件中读取出用户名和密码。此方法下，系统会从文件中逐行读取，读取到行以`username:`开头（不区分大小写）时则认为`:`后均为用户名，读取到行以`password:`开头（不区分大小写）时则认为`:`后均为密码。需要注意的是此方法只能显式的将用户名和密码存储在文件中，并 __不安全__ ，所以不推荐使用本方法。
```
{
    "mcpServers": {
        "mysql_reader": {
            "command": "uv",
            "args": [
                "--directory",
                "Path\to\your\MySQLReader",
                "run",
                "mysql_reader.py",
                "your_database_host",
                "your_database",
                "--authentication-method",
                "file",
                "--file-path",
                "your_file_path"
            ]
        }
    }
}
```
### 3.加密文件efile
当`--authentication-method`传入efile时，系统会从`--file-path`指示的文件中读取出加密后的用户名和密码，然后使用`--private_key_file_name`指示的私钥解密出用户名和密码用以连接数据库。本方法的操作流程如下：
- 1.使用脚本`RSA_key_generator.py`加密用户名和密码。
- 2.将生成的加密数据文件和密钥写入json文件

示例如下：
```
{
    "mcpServers": {
        "mysql_reader": {
            "command": "uv",
            "args": [
                "--directory",
                "Path\to\your\MySQLReader",
                "run",
                "mysql_reader.py",
                "your_database_host",
                "your_database",
                "--authentication-method",
                "file",
                "--file-path",
                "your_enc_file_path",
                "--private_key_file_name"
                "your_pem_file_path"
            ]
        }
    }
}
```
## 加密脚本RSA_key_generator.py的使用方法
```
usage: RSA_key_generator.py [-h] [--use-new-key USE_NEW_KEY]
                            [--public_key_file_name PUBLIC_KEY_FILE_NAME]
                            [--private_key_file_name PRIVATE_KEY_FILE_NAME]
                            [--encrypted_file_name ENCRYPTED_FILE_NAME]
                            username password
```
- `username`，需要加密的用户名。
- `password`，需要加密的密码。
- `--use-new-key`，布尔值，是否使用新的密钥对，如果为true则会生成新密钥对加密，为false则使用
--public_key_file_name指示的公钥加密，默认为true。
- `--public_key_file_name`，公钥文件名，会自动填充.pem后缀名。当`--use-new-key`为true时生成的
新公钥为该名，为false时则读取该路径指示的公钥加密，默认值为public_key.pem。
- `--private_key_file_name`，私钥文件名，会自动填充.pem后缀名。当`--use-new-key`为true时生成的
新私钥为该名，为false时此参数被忽略，默认值为private_key.pem。
- `--encrypted_file_name`，加密后的用户名和密码存储的文件，默认值为config.enc。

__示例：__
- 生成新的密钥对
    - 命令（cmd，Linux需要将`^`换为`\`）：
     ```cmd
      python RSA_key_generator.py your_username your_password ^
    --public_key_file_name your_public_key_file_name ^
    --private_key_file_name your_private_key_file_name ^
    --encrypted_file_name your_encrypted_file_name
    ```
    - 结果：
        生成文件`your_public_key_file_name.pem`、`your_private_key_file_name.pem`和`your_encrypted_file_name.enc`。
- 使用已有密钥对加密（假设已有公钥文件名为`your_public_key_file_name.pem`）
  - 命令（cmd，Linux需要将`^`换为`\`）：
     ```cmd
      python RSA_key_generator.py your_username your_password ^
    --use-new-key false ^
    --public_key_file_name your_public_key_file_name ^
    --encrypted_file_name your_encrypted_file_name
    ```
  - 结果：
      生成文件`your_encrypted_file_name.enc`
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

def generate_key_paris(private_key_name:str="private_key.pem", public_key_name:str="public_key.pem"):
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    # 生成公钥
    public_key = private_key.public_key()
    if not private_key_name.endswith(".pem"):
        private_key_name = private_key_name + ".pem"
    if not public_key_name.endswith(".pem"):
        public_key_name = public_key_name + ".pem"
    # 保存私钥
    with open(private_key_name, "wb") as key_file:
        key_file.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )
    # 保存公钥
    with open(public_key_name, "wb") as key_file:
        key_file.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )
    return private_key,public_key

def encryption_db_user_pwd(username:str, password:str, _public_key:rsa.RSAPublicKey, encrypted_file_name="config.enc"):
    # 加密用户名和密码
    data = username+"pwd:"+password
    encrypted_data = _public_key.encrypt(
        data.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    if not encrypted_file_name.endswith(".enc"):
        encrypted_file_name = encrypted_file_name + ".enc"
    # 将加密后的数据保存到配置文件
    with open(encrypted_file_name, "wb") as config_file:
        config_file.write(encrypted_data)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="加密用户名和密码")
    parser.add_argument(
        "username",
        type=str,
        help="需要加密的用户名"
    )
    parser.add_argument(
        "password",
        type=str,
        help="需要加密的密码"
    )
    parser.add_argument(
        "--use-new-key",
        type=bool,
        default=True,
        help="是否使用新密钥，值为True时生成新密钥且密钥对文件名使用--public_key_file_name和--private_key_file_name。为False时使用--public_key_file_name加密，--private_key_file_name参数无效。"
    )
    parser.add_argument(
        "--public_key_file_name",
        type=str,
        default="public_key.pem",
        help="公钥文件名"
    )
    parser.add_argument(
        "--private_key_file_name",
        type=str,
        default="private_key.pem",
        help="私钥文件名，只有当--use-new-key为True时才生效"
    )
    parser.add_argument(
        "--encrypted_file_name",
        type=str,
        default="config.enc",
        help="加密后的用户名和密码存储的加密文件")
    args = parser.parse_args()
    if args.use_new_key:
        _, public_key = generate_key_paris(args.private_key_file_name,args.public_key_file_name)
    else:
        with open(args.public_key_file_name, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())
    encryption_db_user_pwd(args.username, args.password, public_key, args.encrypted_file_name)

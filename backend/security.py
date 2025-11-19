# backend/security.py
import os
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from jose import jwt, JWTError

# Argon2id：目前主流且安全性高的密碼雜湊演算法
_ph = PasswordHasher()

# 正式環境：必須從環境變數取得密鑰，沒設定就直接報錯
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is not set in environment")

JWT_ALGORITHM = "HS256"
JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))

def hash_password(plain_password: str) -> str:
    """
    將使用者輸入的純文字密碼做 Argon2id 雜湊，回傳可儲存到資料庫的字串。
    """
    return _ph.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    驗證登入時輸入的密碼是否與資料庫中的雜湊相符。
    """
    try:
        return _ph.verify(password_hash, plain_password)
    except VerifyMismatchError:
        # 密碼錯誤
        return False
    except VerificationError:
        # 雜湊格式有問題等其他錯誤，一律當作驗證失敗
        return False

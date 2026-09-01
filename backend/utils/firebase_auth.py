"""
Firebase Authentication & User Security Module for HealthGuard AI
Supports Firebase Auth REST API (SignUp, SignIn, Token Validation)
with automatic fallback to secure salted SHA-256 local database authentication.
"""

import os
import sys
import hashlib
import requests
from typing import Dict, Any, Optional

SECRET_SALT = "HEALTHGUARD_FIREBASE_SALT_2026"


def _get_db():
    """Lazy import of db_manager to avoid circular/stale module caching."""
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _root not in sys.path:
        sys.path.append(_root)
    from database import db_manager as db
    return db


def hash_password(password: str) -> str:
    """Hash password securely using SHA-256 with salt."""
    if not password:
        return ""
    return hashlib.sha256((password + SECRET_SALT).encode('utf-8')).hexdigest()


def get_firebase_api_key() -> str:
    """Retrieve Firebase Web API Key from environment."""
    key = os.getenv("FIREBASE_WEB_API_KEY") or os.getenv("firebase_api_Key") or os.getenv("FIREBASE_API_KEY") or ""
    key = key.strip().strip('"').strip("'").rstrip(",")
    return key


def firebase_sign_up(
    email: str,
    password: str,
    name: str = "User",
    age: int = 40,
    gender: str = "Male",
    weight_kg: float = 70.0,
    height_cm: float = 170.0,
    blood_group: str = "O+"
) -> Dict[str, Any]:
    """
    Register a new user via Firebase Auth REST API or local secure authentication.

    Returns:
        Dict with keys: 'success', 'user_id', 'email', 'name', 'message', 'provider'
    """
    db = _get_db()

    email_clean = email.strip().lower()
    if not email_clean or len(password) < 6:
        return {"success": False, "message": "Email and password (min 6 chars) are required."}

    existing_user = db.get_user_by_email(email_clean)
    if existing_user:
        return {"success": False, "message": "An account with this email already exists."}

    api_key = get_firebase_api_key()
    firebase_uid = None
    id_token = None
    provider_used = "Local Database"

    if api_key and not api_key.startswith("your_"):
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
            payload = {
                "email": email_clean,
                "password": password,
                "returnSecureToken": True
            }
            response = requests.post(url, json=payload, timeout=5)
            res_data = response.json()

            if response.status_code == 200:
                firebase_uid = res_data.get("localId")
                id_token = res_data.get("idToken")
                provider_used = "Firebase Cloud Auth"
            else:
                error_msg = res_data.get("error", {}).get("message", "Firebase Auth error")
                if "EMAIL_EXISTS" in error_msg:
                    return {"success": False, "message": "This email is already registered on Firebase Auth."}
        except Exception:
            pass  # Fallback to local authentication seamlessly

    # Save user to database
    pwd_hash = hash_password(password)
    user_id = db.create_user(
        name=name,
        age=age,
        gender=gender,
        weight_kg=weight_kg,
        height_cm=height_cm,
        blood_group=blood_group,
        email=email_clean,
        password_hash=pwd_hash,
        firebase_uid=firebase_uid
    )

    return {
        "success": True,
        "user_id": user_id,
        "email": email_clean,
        "name": name,
        "firebase_uid": firebase_uid,
        "id_token": id_token,
        "provider": provider_used,
        "message": f"Account successfully created via {provider_used}!"
    }


def firebase_sign_in(email: str, password: str) -> Dict[str, Any]:
    """
    Authenticate user via Firebase Auth REST API or local database fallback.
    Supports login via email or username.

    Returns:
        Dict with keys: 'success', 'user_id', 'email', 'name', 'message', 'provider'
    """
    db = _get_db()

    email_clean = email.strip()
    if not email_clean or not password:
        return {"success": False, "message": "Please enter both email/username and password."}

    api_key = get_firebase_api_key()
    provider_used = "Local Database"
    id_token = None
    firebase_uid = None

    # Try Firebase Auth if email is formatted and API key is present
    if api_key and not api_key.startswith("your_") and "@" in email_clean:
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
            payload = {
                "email": email_clean.lower(),
                "password": password,
                "returnSecureToken": True
            }
            response = requests.post(url, json=payload, timeout=5)
            res_data = response.json()

            if response.status_code == 200:
                firebase_uid = res_data.get("localId")
                id_token = res_data.get("idToken")
                provider_used = "Firebase Cloud Auth"

                local_user = db.get_user_by_email(email_clean.lower())
                if not local_user:
                    user_id = db.create_user(
                        name=email_clean.split("@")[0].title(),
                        email=email_clean.lower(),
                        password_hash=hash_password(password),
                        firebase_uid=firebase_uid
                    )
                    local_user = db.get_user(user_id)

                return {
                    "success": True,
                    "user_id": local_user["id"],
                    "email": local_user.get("email", email_clean),
                    "name": local_user.get("name", "User"),
                    "firebase_uid": firebase_uid,
                    "id_token": id_token,
                    "provider": provider_used,
                    "message": "Logged in successfully via Firebase Cloud Auth!"
                }
        except Exception:
            pass  # Fallback to local authentication

    # Local SQLite Authentication fallback (supports email or username)
    pwd_hash = hash_password(password)
    local_user = db.authenticate_user_db(email_clean, pwd_hash)

    if not local_user:
        # Check if user exists by email or name without a password hash yet (legacy/demo profile)
        legacy_user = db.get_user_by_email_or_name(email_clean)
        if legacy_user:
            # If user has no password set, set their password now and log them in
            if not legacy_user.get("password_hash"):
                db.update_user(legacy_user["id"], password_hash=pwd_hash)
                local_user = db.get_user(legacy_user["id"])
            elif legacy_user.get("password_hash") == pwd_hash:
                local_user = legacy_user

    if local_user:
        return {
            "success": True,
            "user_id": local_user["id"],
            "email": local_user.get("email", email_clean),
            "name": local_user.get("name", "User"),
            "provider": provider_used,
            "message": f"Welcome back, {local_user.get('name', 'User')}! Logged in successfully."
        }
    else:
        return {"success": False, "message": "Invalid credentials. Please check your email/username and password."}

"""Firebase Authentication module using REST API."""

import os
import logging
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available (e.g., on Android), use environment variables directly
    pass

try:
    import httpx
except ImportError:
    httpx = None
    logging.warning("httpx not available. Firebase authentication will not work.")

logger = logging.getLogger(__name__)


class FirebaseAuth:
    """Firebase Authentication handler using REST API."""
    
    _api_key: Optional[str] = None
    _project_id: Optional[str] = None
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase with API key from environment, config file, or local storage."""
        # Use the config loader which tries multiple sources
        from .firebase_config import load_firebase_config
        cls._api_key, cls._project_id = load_firebase_config()
        
        if not cls._api_key:
            logger.warning("FIREBASE_API_KEY not found. Please configure Firebase credentials.")
        if not cls._project_id:
            logger.warning("FIREBASE_PROJECT_ID not found. Please configure Firebase credentials.")
    
    @classmethod
    def set_credentials(cls, api_key: str, project_id: str):
        """Set Firebase credentials and save to local storage."""
        cls._api_key = api_key
        cls._project_id = project_id
        
        # Save to local storage for persistence
        try:
            from .local_storage import LocalStorage
            LocalStorage.save_preference("firebase_api_key", api_key)
            LocalStorage.save_preference("firebase_project_id", project_id)
            logger.info("Firebase credentials saved to local storage")
        except ImportError:
            pass
    
    @classmethod
    def _get_auth_url(cls, endpoint: str) -> str:
        """Get Firebase Auth REST API URL."""
        if not cls._api_key:
            cls.initialize()
        
        base_url = "https://identitytoolkit.googleapis.com/v1"
        return f"{base_url}/{endpoint}?key={cls._api_key}"
    
    @classmethod
    async def sign_up(cls, email: str, password: str) -> tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        Sign up a new user with email and password.
        
        Args:
            email: User email address
            password: User password
            
        Returns:
            Tuple of (success: bool, user_id: Optional[str], token: Optional[str], error_message: Optional[str])
        """
        if not cls._api_key:
            cls.initialize()
        
        if not cls._api_key:
            return False, None, None, "Firebase API key not configured. Please configure Firebase credentials."
        
        if httpx is None:
            return False, None, None, "httpx library not available. Please install dependencies."
        
        try:
            url = cls._get_auth_url("accounts:signUp")
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                data = response.json()
                
                if response.status_code == 200:
                    user_id = data.get("localId")
                    token = data.get("idToken")
                    logger.info(f"User created successfully: {user_id}")
                    return True, user_id, token, None
                else:
                    error_msg = data.get("error", {}).get("message", "Unknown error")
                    logger.error(f"Sign up error: {error_msg}")
                    return False, None, None, cls._format_error_message(error_msg)
                    
        except Exception as e:
            logger.error(f"Sign up exception: {e}")
            return False, None, None, f"Failed to create account: {str(e)}"
    
    @classmethod
    async def sign_in(cls, email: str, password: str) -> tuple[bool, Optional[str], Optional[str], Optional[str]]:
        """
        Sign in a user with email and password.
        
        Args:
            email: User email address
            password: User password
            
        Returns:
            Tuple of (success: bool, user_id: Optional[str], token: Optional[str], error_message: Optional[str])
        """
        if not cls._api_key:
            cls.initialize()
        
        if not cls._api_key:
            return False, None, None, "Firebase API key not configured. Please configure Firebase credentials."
        
        if httpx is None:
            return False, None, None, "httpx library not available. Please install dependencies."
        
        try:
            url = cls._get_auth_url("accounts:signInWithPassword")
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload)
                data = response.json()
                
                if response.status_code == 200:
                    user_id = data.get("localId")
                    token = data.get("idToken")
                    logger.info(f"User signed in successfully: {user_id}")
                    return True, user_id, token, None
                else:
                    error_msg = data.get("error", {}).get("message", "Unknown error")
                    logger.error(f"Sign in error: {error_msg}")
                    return False, None, None, cls._format_error_message(error_msg)
                    
        except Exception as e:
            logger.error(f"Sign in exception: {e}")
            return False, None, None, f"Failed to sign in: {str(e)}"
    
    @classmethod
    def _format_error_message(cls, error_msg: str) -> str:
        """Format Firebase error messages to user-friendly text."""
        error_mapping = {
            "EMAIL_EXISTS": "An account with this email already exists.",
            "EMAIL_NOT_FOUND": "No account found with this email address.",
            "INVALID_PASSWORD": "Invalid password.",
            "USER_DISABLED": "This account has been disabled.",
            "INVALID_EMAIL": "Invalid email address.",
            "WEAK_PASSWORD": "Password should be at least 6 characters.",
            "OPERATION_NOT_ALLOWED": "This operation is not allowed.",
        }
        return error_mapping.get(error_msg, error_msg.replace("_", " ").title())


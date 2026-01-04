"""Firebase Authentication module using REST API."""

import os
import json
import logging
from typing import Optional
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class FirebaseAuth:
    """Firebase Authentication handler using REST API."""
    
    _api_key: Optional[str] = None
    _project_id: Optional[str] = None
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase with API key from environment."""
        cls._api_key = os.getenv("FIREBASE_API_KEY")
        cls._project_id = os.getenv("FIREBASE_PROJECT_ID")
        
        if not cls._api_key:
            logger.warning("FIREBASE_API_KEY not found in environment variables")
        if not cls._project_id:
            logger.warning("FIREBASE_PROJECT_ID not found in environment variables")
    
    @classmethod
    def _get_auth_url(cls, endpoint: str) -> str:
        """Get Firebase Auth REST API URL."""
        if not cls._api_key:
            cls.initialize()
        
        base_url = "https://identitytoolkit.googleapis.com/v1"
        return f"{base_url}/{endpoint}?key={cls._api_key}"
    
    @classmethod
    async def sign_up(cls, email: str, password: str) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Sign up a new user with email and password.
        
        Args:
            email: User email address
            password: User password
            
        Returns:
            Tuple of (success: bool, user_id: Optional[str], error_message: Optional[str])
        """
        if not cls._api_key:
            cls.initialize()
        
        if not cls._api_key:
            return False, None, "Firebase API key not configured. Please check your .env file."
        
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
                    logger.info(f"User created successfully: {user_id}")
                    return True, user_id, None
                else:
                    error_msg = data.get("error", {}).get("message", "Unknown error")
                    logger.error(f"Sign up error: {error_msg}")
                    return False, None, cls._format_error_message(error_msg)
                    
        except Exception as e:
            logger.error(f"Sign up exception: {e}")
            return False, None, f"Failed to create account: {str(e)}"
    
    @classmethod
    async def sign_in(cls, email: str, password: str) -> tuple[bool, Optional[str], Optional[str]]:
        """
        Sign in a user with email and password.
        
        Args:
            email: User email address
            password: User password
            
        Returns:
            Tuple of (success: bool, user_id: Optional[str], error_message: Optional[str])
        """
        if not cls._api_key:
            cls.initialize()
        
        if not cls._api_key:
            return False, None, "Firebase API key not configured. Please check your .env file."
        
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
                    id_token = data.get("idToken")
                    logger.info(f"User signed in successfully: {user_id}")
                    # Store token for future use if needed
                    return True, user_id, None
                else:
                    error_msg = data.get("error", {}).get("message", "Unknown error")
                    logger.error(f"Sign in error: {error_msg}")
                    return False, None, cls._format_error_message(error_msg)
                    
        except Exception as e:
            logger.error(f"Sign in exception: {e}")
            return False, None, f"Failed to sign in: {str(e)}"
    
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


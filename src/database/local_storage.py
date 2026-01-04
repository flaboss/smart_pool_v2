"""Simple local storage for user preferences and authentication."""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

# Session expiration: 30 days
SESSION_EXPIRY_DAYS = 30

# Cache for storage file path
_storage_file_cache = None


def _get_storage_path():
    """Get storage path that works on all platforms including Android."""
    global _storage_file_cache
    if _storage_file_cache is not None:
        return _storage_file_cache
    
    try:
        # Try to use app-specific directory (works on Android)
        app_data_dir = os.getenv("FLET_APP_DATA_DIR")
        if app_data_dir:
            storage_dir = Path(app_data_dir) / "smart_pool_v2"
            storage_dir.mkdir(parents=True, exist_ok=True)
            _storage_file_cache = storage_dir / "user_data.json"
            return _storage_file_cache
    except Exception:
        pass
    
    try:
        # Fallback to home directory (works on desktop)
        storage_dir = Path.home() / ".smart_pool_v2"
        storage_dir.mkdir(parents=True, exist_ok=True)
        _storage_file_cache = storage_dir / "user_data.json"
        return _storage_file_cache
    except Exception:
        # Last resort: use current directory
        _storage_file_cache = Path("user_data.json")
        return _storage_file_cache


class LocalStorage:
    """Simple local storage using JSON file."""
    
    @staticmethod
    def _load_data() -> Dict[str, Any]:
        """Load data from storage file."""
        try:
            storage_file = _get_storage_path()
            if not storage_file.exists():
                return {}
            
            with open(storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, OSError, PermissionError, Exception) as e:
            # If file is corrupted or inaccessible, return empty dict
            print(f"Error loading storage: {e}")
            return {}
    
    @staticmethod
    def _save_data(data: Dict[str, Any]):
        """Save data to storage file."""
        try:
            storage_file = _get_storage_path()
            # Ensure parent directory exists
            storage_file.parent.mkdir(parents=True, exist_ok=True)
            with open(storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except (IOError, OSError, PermissionError, Exception) as e:
            print(f"Error saving data: {e}")
    
    @staticmethod
    def save_auth(user_id: str, email: str):
        """Save authentication data with current timestamp."""
        data = LocalStorage._load_data()
        data['auth'] = {
            'user_id': user_id,
            'email': email,
            'login_timestamp': datetime.now().isoformat()
        }
        LocalStorage._save_data(data)
    
    @staticmethod
    def get_auth() -> Optional[Dict[str, str]]:
        """Get authentication data if still valid (within 30 days)."""
        data = LocalStorage._load_data()
        
        if 'auth' not in data:
            return None
        
        auth = data['auth']
        login_timestamp_str = auth.get('login_timestamp')
        
        if not login_timestamp_str:
            return None
        
        try:
            login_timestamp = datetime.fromisoformat(login_timestamp_str)
            expiry_date = login_timestamp + timedelta(days=SESSION_EXPIRY_DAYS)
            
            # Check if session is still valid
            if datetime.now() > expiry_date:
                # Session expired, clear auth
                LocalStorage.clear_auth()
                return None
            
            return {
                'user_id': auth.get('user_id'),
                'email': auth.get('email')
            }
        except (ValueError, KeyError):
            return None
    
    @staticmethod
    def clear_auth():
        """Clear authentication data."""
        data = LocalStorage._load_data()
        if 'auth' in data:
            del data['auth']
            LocalStorage._save_data(data)
    
    @staticmethod
    def save_preference(key: str, value: Any):
        """Save a user preference."""
        data = LocalStorage._load_data()
        
        if 'preferences' not in data:
            data['preferences'] = {}
        
        data['preferences'][key] = value
        LocalStorage._save_data(data)
    
    @staticmethod
    def get_preference(key: str, default: Any = None) -> Any:
        """Get a user preference."""
        data = LocalStorage._load_data()
        return data.get('preferences', {}).get(key, default)
    
    @staticmethod
    def get_all_preferences() -> Dict[str, Any]:
        """Get all user preferences."""
        data = LocalStorage._load_data()
        return data.get('preferences', {})
    
    @staticmethod
    def save_preferences(preferences: Dict[str, Any]):
        """Save multiple preferences at once."""
        data = LocalStorage._load_data()
        data['preferences'] = preferences
        LocalStorage._save_data(data)


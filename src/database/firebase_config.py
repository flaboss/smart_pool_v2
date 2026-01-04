"""Firebase configuration loader for Android and other platforms."""

import json
import os
import sys
from pathlib import Path
from typing import Optional, Tuple


def load_firebase_config() -> Tuple[Optional[str], Optional[str]]:
    """
    Load Firebase configuration from multiple sources in order of priority:
    1. Environment variables (desktop/web)
    2. Config file in app directory (Android/mobile)
    3. Local storage (if previously saved)
    
    Returns:
        Tuple of (api_key, project_id)
    """
    api_key = None
    project_id = None
    
    # 1. Try environment variables first (works on desktop/web)
    api_key = os.getenv("FIREBASE_API_KEY")
    project_id = os.getenv("FIREBASE_PROJECT_ID")
    
    if api_key and project_id:
        return api_key, project_id
    
    # 2. Try config file in app directory (works on Android)
    try:
        # Get the directory where this file is located
        current_file = Path(__file__).resolve()
        src_dir = current_file.parent.parent  # Go up from database/ to src/
        root_dir = src_dir.parent  # Go up from src/ to root/
        
        # Try multiple paths where config might be located
        config_paths = [
            src_dir / "firebase_config.json",  # src/firebase_config.json (recommended for Android)
            root_dir / "firebase_config.json",  # root/firebase_config.json
            current_file.parent / "firebase_config.json",  # database/firebase_config.json
            Path("firebase_config.json"),  # Current working directory
        ]
        
        # Also try paths relative to sys.executable (for bundled apps)
        if hasattr(sys, '_MEIPASS'):  # PyInstaller bundle
            config_paths.insert(0, Path(sys._MEIPASS) / "firebase_config.json")
        
        # Try paths relative to the main script
        if hasattr(sys, 'argv') and len(sys.argv) > 0:
            main_script = Path(sys.argv[0]).resolve()
            if main_script.exists():
                config_paths.extend([
                    main_script.parent / "firebase_config.json",
                    main_script.parent.parent / "firebase_config.json",
                ])
        
        for config_path in config_paths:
            try:
                if config_path.exists():
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        api_key = config.get("api_key") or config.get("FIREBASE_API_KEY")
                        project_id = config.get("project_id") or config.get("FIREBASE_PROJECT_ID")
                        if api_key and project_id:
                            print(f"Firebase config loaded from: {config_path}")
                            return api_key, project_id
            except (json.JSONDecodeError, IOError, OSError) as e:
                print(f"Error reading config from {config_path}: {e}")
                continue
    except Exception as e:
        print(f"Error searching for config file: {e}")
    
    # 3. Try local storage (if previously configured)
    try:
        from .local_storage import LocalStorage
        api_key = LocalStorage.get_preference("firebase_api_key")
        project_id = LocalStorage.get_preference("firebase_project_id")
        if api_key and project_id:
            print("Firebase config loaded from local storage")
            return api_key, project_id
    except Exception as e:
        print(f"Error loading from local storage: {e}")
    
    return None, None


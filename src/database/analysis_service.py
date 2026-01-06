from datetime import datetime
import uuid
from typing import List, Dict, Any
from .local_storage import LocalStorage
from .firebase_db import FirebaseDB

class AnalysisService:
    """Service for managing pool analysis data."""

    @staticmethod
    def get_analyses(user_id: str) -> List[Dict[str, Any]]:
        """Get all analyses for a user."""
        key = f"analysis_{user_id}"
        return LocalStorage.get_preference(key, [])

    @staticmethod
    async def save_analysis(user_id: str, analysis_data: Dict[str, Any]) -> bool:
        """Save analysis result."""
        try:
            analyses = AnalysisService.get_analyses(user_id)
            
            # Add metadata
            analysis_data['id'] = str(uuid.uuid4())
            analysis_data['created_at'] = datetime.now().isoformat()
            
            analyses.append(analysis_data)
            
            key = f"analysis_{user_id}"
            LocalStorage.save_preference(key, analyses)
            
            # Sync to Firebase
            try:
                auth = LocalStorage.get_auth()
                if auth and auth.get('token'):
                    # We don't save the image path to Firebase, logic should handle data stripping if needed
                    # For now passing as is, assuming valid JSON types
                    await FirebaseDB.save_analysis(user_id, analysis_data, auth.get('token'))
            except Exception as e:
                print(f"Error syncing analysis to Firebase: {e}")
            
            return True
        except Exception as e:
            print(f"Error saving analysis: {e}")
            return False

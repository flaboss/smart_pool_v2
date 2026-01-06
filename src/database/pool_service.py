from datetime import datetime
import uuid
from typing import List, Dict, Any, Optional
from .local_storage import LocalStorage

from .firebase_db import FirebaseDB

class PoolService:
    """Service for managing user pools."""

    @staticmethod
    def get_pools(user_id: str) -> List[Dict[str, Any]]:
        """Get all pools for a user."""
        key = f"pools_{user_id}"
        return LocalStorage.get_preference(key, [])

    @staticmethod
    async def save_pool(user_id: str, pool_data: Dict[str, Any]) -> bool:
        """Save or update a pool."""
        try:
            pools = PoolService.get_pools(user_id)
            
            # If pool has ID, it's an update, otherwise create new
            pool_id = pool_data.get('id')
            
            if pool_id:
                # Update existing
                for i, pool in enumerate(pools):
                    if pool.get('id') == pool_id:
                        # Keep created_at from existing if not provided
                        if 'created_at' not in pool_data and 'created_at' in pool:
                            pool_data['created_at'] = pool['created_at']
                        
                        pool_data['updated_at'] = datetime.now().isoformat()
                        pools[i] = {**pool, **pool_data}
                        break
                else:
                    pools.append(pool_data)
            else:
                # Create new
                pool_data['id'] = str(uuid.uuid4())
                pool_data['created_at'] = datetime.now().isoformat()
                pool_data['updated_at'] = datetime.now().isoformat()
                pools.append(pool_data)
            
            key = f"pools_{user_id}"
            LocalStorage.save_preference(key, pools)
            
            # Sync to Firebase
            try:
                auth = LocalStorage.get_auth()
                if auth and auth.get('token'):
                    await FirebaseDB.save_pool(user_id, pool_data, auth.get('token'))
            except Exception as e:
                print(f"Error syncing to Firebase: {e}")
            
            return True
        except Exception as e:
            print(f"Error saving pool: {e}")
            return False

    @staticmethod
    async def delete_pool(user_id: str, pool_id: str) -> bool:
        """Delete a pool."""
        try:
            pools = PoolService.get_pools(user_id)
            new_pools = [p for p in pools if p.get('id') != pool_id]
            
            if len(new_pools) != len(pools):
                key = f"pools_{user_id}"
                LocalStorage.save_preference(key, new_pools)
                
                # Sync to Firebase
                try:
                    auth = LocalStorage.get_auth()
                    if auth and auth.get('token'):
                        await FirebaseDB.delete_pool(user_id, pool_id, auth.get('token'))
                except Exception as e:
                    print(f"Error syncing delete to Firebase: {e}")
                
                return True
            return False
        except Exception as e:
            print(f"Error deleting pool: {e}")
            return False

    @staticmethod
    async def sync_pools(user_id: str) -> None:
        """Fetch pools from Firebase and merge with local storage."""
        try:
            auth = LocalStorage.get_auth()
            if not auth or not auth.get('token'):
                return

            remote_pools = await FirebaseDB.get_pools(user_id, auth.get('token'))
            if not remote_pools:
                return

            local_pools = PoolService.get_pools(user_id)
            local_map = {p.get('id'): p for p in local_pools}
            
            # Merge strategy: Remote fields overwrite local if ID matches
            # Also add new pools from remote
            updated = False
            for remote_pool in remote_pools:
                pool_id = remote_pool.get('id')
                if not pool_id:
                    continue
                
                if pool_id in local_map:
                    # Check if actually different? For now, just overwrite to be safe
                    # ideally we check updated_at but let's assume remote is truth for now 
                    # as user compliant about missing data.
                    local_map[pool_id] = remote_pool
                    updated = True
                else:
                    local_map[pool_id] = remote_pool
                    updated = True
            
            if updated:
                new_list = list(local_map.values())
                key = f"pools_{user_id}"
                LocalStorage.save_preference(key, new_list)
                print(f"Synced {len(new_list)} pools (merged local and remote).")
                
        except Exception as e:
            print(f"Error syncing pools: {e}")

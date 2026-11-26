from django.core.cache import cache 



def _version_key(user_id):
    """name of the cache entry that stores a user's 'version' number"""
    return f"peer_request:version:{user_id}"

def _get_version(user_id):
    """return the user's current cache version (reates it as 1 if missing)"""
    #get or set, read it, or store 1 if it doesn't exist : timeout=None=nver expire 
    return cache.get_or_set(_version_key(user_id),1,timeout=None)

def bump_version(user_id):
    """invalidate all cache pages for user by moving to a new version"""
    try:
        cache.incr(_version_key(user_id))
    except ValueError:
        cache.set(_version_key(user_id),2,timeout=None)
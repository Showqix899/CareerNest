from django.core.cache import cache 



def _version_key(user_id,tag):
    """name of the cache entry that stores a user's 'version' number"""
    return f"{tag}:version:{user_id}"

def _get_version(user_id,tag):
    """return the user's current cache version (reates it as 1 if missing)"""
    #get or set, read it, or store 1 if it doesn't exist : timeout=None=nver expire 
    return cache.get_or_set(_version_key(user_id,tag),1,timeout=None)

def bump_version(user_id,tag):
    """invalidate all cache pages for user by moving to a new version"""
    try:
        cache.incr(_version_key(user_id,tag))
    except ValueError:
        cache.set(_version_key(user_id,tag),2,timeout=None)
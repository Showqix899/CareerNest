from rest_framework_simplejwt.tokens import RefreshToken


"""generate refressh tokens and add extra information to the token"""
def get_tokens_for_user(user):
    
    """creates jwt token for a user """
    
    refresh = RefreshToken.for_user(user)
    
    #add extra info to the token 
    refresh["email"]=user.email
    refresh["full_name"]=user.full_name
    
    
    return {
        "refresh":str(refresh),
        "access":str(refresh.access_token)
    }
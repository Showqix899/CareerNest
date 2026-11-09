from functools import wraps
from django.shortcuts import render,redirect



def admin_required(view_func):
    
    """
    custom decorator to restrict views to staff members or superusers.
    sage:@admin_required
    """
    @wraps(view_func)
    def wrapper(request,*args,**kwargs):
        #if the user is authenticated or not 
        if not request.user.is_authenticated:
            return redirect("accounts:user_login")
        
        #if the user staff or super user
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request,*args,**kwargs)
        
        return render(request, "user_profile/error.html", {
            "message": "Access denied. Admin privileges are required to view this page."
        })
        
    return wrapper
    
    
    
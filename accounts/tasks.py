from celery import shared_task
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.html import escape
from django.utils.http import urlsafe_base64_encode


from .models import User

def build_activation_link(user):
    
    """
    generates activation link
    it encode users uuid and put it in a url
    """
    #safe encoding to user uuid
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    #create secure token fro this user
    token = default_token_generator.make_token(user)
    
    #reverse("activate") builds the path using the url name "activte"
    #(we define this url in urls.py)
    path = reverse("activate",kwargs={"uidb64":uid,"token":token})
    
    return f"{settings.SITE_URL}{path}"




def build_email_html(full_name, activation_link):
    """Return the professional HTML version of the email."""

    # escape() makes the name safe, so special characters can't break the HTML
    name = escape(full_name)
    site_name = escape(settings.SITE_NAME)

    # Email clients ignore most CSS files, so styles are written inline
    return f"""
    <div style="background-color:#f4f6f8; padding:30px 0; font-family:Arial, Helvetica, sans-serif;">
      <table align="center" width="100%" style="max-width:560px; background:#ffffff; border-radius:8px; padding:32px;">
        <tr>
          <td>
            <h2 style="margin:0 0 16px 0; color:#1f2937;">Verify your email address</h2>
            <p style="color:#374151; font-size:15px; line-height:1.6;">Hi {name},</p>
            <p style="color:#374151; font-size:15px; line-height:1.6;">
              Thank you for registering with {site_name}.
              Please confirm your email address to activate your account.
            </p>
            <p style="text-align:center; margin:32px 0;">
              <a href="{activation_link}"
                 style="background-color:#2563eb; color:#ffffff; padding:12px 28px;
                        text-decoration:none; border-radius:6px; font-size:15px;
                        font-weight:bold; display:inline-block;">
                Activate my account
              </a>
            </p>
            <p style="color:#6b7280; font-size:13px; line-height:1.6;">
              If the button does not work, copy and paste this link into your browser:<br>
              <a href="{activation_link}" style="color:#2563eb; word-break:break-all;">{activation_link}</a>
            </p>
            <hr style="border:none; border-top:1px solid #e5e7eb; margin:24px 0;">
            <p style="color:#9ca3af; font-size:12px; line-height:1.6;">
              This link will expire in a few days. If you did not create an account,
              you can safely ignore this email.
            </p>
          </td>
        </tr>
      </table>
    </div>
    """
    
    
@shared_task(bind=True,max_retries=3)
def send_verification_email(self,user_id):
    
    """send the acount activation url link to the users email"""
    
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return
    
    if user.is_active:
        return
    
    activation_link = build_activation_link(user)
    
    subject = f"Verify your email for {settings.SITE_NAME}"
    
    text_body = (
        f"Hi {user.full_name}, \n\n"
        f"Thanke your for registering wit {settings.SITE_NAME}.\n"
        f"Please activate your account by opening this link: \n\n"
        f"{activation_link}\n\n"
        f"if you did not create an account, you can ignore this email"
    )
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email = settings.DEFAULT_FROM_EMAIL,
        to={user.email}
    )
    
    try:
        email.send()
    except Exception as exc:
        #sending failed wait 60 secode theny try again 
        raise self.retry(exc=exc, countdown=60)
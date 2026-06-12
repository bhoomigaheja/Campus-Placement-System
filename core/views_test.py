from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

def test_email_view(request):
    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')
        to_email = request.GET.get('to', 'gahejabhumigaheja@gmail.com')
        
        send_mail(
            subject='CareerConnect Email Diagnostic Test',
            message=f'This is a test email sent from {from_email}. If you receive this, SendGrid is working perfectly!',
            from_email=from_email,
            recipient_list=[to_email],
            fail_silently=False,
        )
        return HttpResponse(f"✅ SUCCESS! Email was successfully sent from {from_email} to {to_email}.")
    except Exception as e:
        import traceback
        return HttpResponse(f"❌ ERROR SENDING EMAIL:<br><br><b>{str(e)}</b><br><br><pre>{traceback.format_exc()}</pre>")

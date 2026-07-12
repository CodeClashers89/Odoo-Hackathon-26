from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.urls import resolve
from django.contrib.auth.signals import user_login_failed, user_logged_in
from django.dispatch import receiver

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class LoginLockoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Resolve path to check if we are hitting the login view
        try:
            resolved = resolve(request.path_info)
            is_login_view = resolved.url_name == 'login'
        except Exception:
            is_login_view = False

        if is_login_view and request.method == 'POST':
            ip = get_client_ip(request)
            attempts = cache.get(f'login_attempts_{ip}', 0)
            if attempts >= 5:
                html_content = """
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Device Blocked - TransitOps</title>
                    <link rel="preconnect" href="https://fonts.googleapis.com">
                    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
                    <style>
                        body {
                            font-family: 'Inter', -apple-system, sans-serif;
                            background-color: #F7F8FA;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            height: 100vh;
                            margin: 0;
                            color: #1A1A2E;
                        }
                        .error-card {
                            background: white;
                            padding: 40px;
                            border-radius: 12px;
                            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                            max-width: 450px;
                            text-align: center;
                            border: 1px solid #E5E7EB;
                        }
                        h1 {
                            color: #EF4444;
                            font-size: 24px;
                            margin-bottom: 16px;
                            font-weight: 700;
                        }
                        p {
                            color: #6B7280;
                            font-size: 14px;
                            line-height: 1.6;
                            margin-bottom: 24px;
                        }
                        .timer-badge {
                            background-color: rgba(239, 68, 68, 0.1);
                            color: #EF4444;
                            padding: 8px 16px;
                            border-radius: 9999px;
                            font-weight: 600;
                            font-size: 13px;
                            display: inline-block;
                        }
                    </style>
                </head>
                <body>
                    <div class="error-card">
                        <h1>Temporarily Blocked</h1>
                        <p>Too many failed login attempts have been detected from this device. To protect system security, login access has been temporarily disabled.</p>
                        <div class="timer-badge">Please try again in 5 minutes</div>
                    </div>
                </body>
                </html>
                """
                return HttpResponseForbidden(html_content)

        response = self.get_response(request)
        return response

@receiver(user_login_failed)
def increment_login_attempts(sender, credentials, request, **kwargs):
    if request:
        ip = get_client_ip(request)
        attempts = cache.get(f'login_attempts_{ip}', 0)
        cache.set(f'login_attempts_{ip}', attempts + 1, timeout=300) # lock out for 5 minutes (300s)

@receiver(user_logged_in)
def reset_login_attempts(sender, request, user, **kwargs):
    if request:
        ip = get_client_ip(request)
        cache.delete(f'login_attempts_{ip}')

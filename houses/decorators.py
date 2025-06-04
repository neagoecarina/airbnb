from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required



def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            return view_func(request, *args, **kwargs)

        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="UTF-8">
          <title>Access Denied</title>
          <style>
            body {
              font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
              background-color: #f8f9fa;
              display: flex;
              align-items: center;
              justify-content: center;
              height: 100vh;
              margin: 0;
            }
            .forbidden-box {
              background: white;
              padding: 2rem 2.5rem;
              border-radius: 12px;
              box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
              text-align: center;
            }
            h1 {
              color: #dc3545;
              margin-bottom: 1rem;
            }
            p {
              color: #555;
              margin-bottom: 2rem;
            }
            a {
              text-decoration: none;
              background-color: #007bff;
              color: white;
              padding: 0.6rem 1.2rem;
              border-radius: 8px;
              font-size: 1rem;
              transition: background-color 0.3s ease;
            }
            a:hover {
              background-color: #0056b3;
            }
          </style>
        </head>
        <body>
          <div class="forbidden-box">
            <h1>403 - Forbidden</h1>
            <p>You do not have permission to access this page.</p>
            <a href="javascript:history.back()">Go Back</a>
          </div>
        </body>
        </html>
        """
        return HttpResponseForbidden(html)

    return _wrapped_view

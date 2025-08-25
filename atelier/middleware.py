from django.shortcuts import redirect
from django.urls import reverse

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Пути, которые доступны без аутентификации
        public_paths = [
            reverse('login'),
            reverse('register'),
        ]

        if not request.user.is_authenticated and request.path not in public_paths:
            return redirect('login')

        response = self.get_response(request)
        return response
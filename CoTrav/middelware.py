from django.shortcuts import render, redirect
from django.utils.deprecation import MiddlewareMixin


class AuthRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):

        context = {}
        if not request.user.is_authenticated:
            context['error'] = "You Are Not Login ... Please Login"
            return render(request, 'corporate_login.html', context)
        else:
            return None

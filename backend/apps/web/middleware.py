"""Blocks all access until the software is activated with the install key."""
from django.shortcuts import redirect

from .activation import is_activated


class ActivationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not is_activated():
            p = request.path
            allowed = (p.startswith('/activate')
                       or p.startswith('/static')
                       or p.startswith('/media'))
            if not allowed:
                return redirect('web:activate')
        return self.get_response(request)

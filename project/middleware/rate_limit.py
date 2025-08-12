from django.core.cache import cache
from django.http import JsonResponse
import time

class RateLimitMiddleware:

    RATE_LIMIT = 100
    TIME_WINDOW = 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self.get_client_ip(request)
        if ip:
            cache_key = f"rl:{ip}"
            request_times = cache.get(cache_key, [])

            now = time.time()
            request_times = [t for t in request_times if now - t < self.TIME_WINDOW]

            if len(request_times) >= self.RATE_LIMIT:
                return JsonResponse(
                    {"detail": "Too many requests, please try again later."},
                    status=429
                )

            request_times.append(now)
            cache.set(cache_key, request_times, timeout=self.TIME_WINDOW)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')

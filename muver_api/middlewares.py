from django.contrib.auth import logout


class ActiveUserMiddleware(object):
    def process_request(self, request):
        if not request.user.is_authenticated():
            return
        elif not request.user.is_active:
           logout(request)
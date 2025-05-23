import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

class IconViewSet(APIView):
    """
    GET /lists/icons/ → returns all icon filenames + URLs.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        icons_dir = os.path.join(settings.MEDIA_ROOT, 'lists/icons')
        files = []
        for fname in os.listdir(icons_dir):
            if os.path.isfile(os.path.join(icons_dir, fname)):
                files.append({
                    'filename': fname,
                    'url': request.build_absolute_uri(
                        settings.MEDIA_URL + f'lists/icons/{fname}'
                    )
                })
        return Response({
            'icons': files
        })
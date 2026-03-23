"""Inject template variables used site-wide."""
from django.conf import settings


def asset_version(_request):
    """Bust browser cache for static files when we bump STATIC_ASSET_VERSION."""
    return {
        "STATIC_ASSET_VERSION": getattr(settings, "STATIC_ASSET_VERSION", "1"),
    }

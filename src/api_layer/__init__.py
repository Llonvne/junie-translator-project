"""
API层 (API Layer)
接受来自于实体层的实体，并将接口通过网络开放
"""

from .app import create_app
from .routes import register_routes

__all__ = [
    'create_app',
    'register_routes'
]
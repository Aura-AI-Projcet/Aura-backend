"""
Services Module

Centralized access to all service instances.
"""

from .chat import ChatService  # Import the class
from .compatibility import compatibility_service
from .fortune import fortune_service
from .onboarding import onboarding_service

chat_service = ChatService()  # Instantiate the service

__all__ = [
    "compatibility_service",
    "fortune_service",
    "onboarding_service",
    "chat_service",
]

"""
MLOps Core - Common utilities and base classes for MLOps projects
"""

__version__ = "1.0.0"
__author__ = "MLOps Team"

from .logging import get_logger
from .exceptions import MLOpsException

__all__ = ["get_logger", "MLOpsException"] 
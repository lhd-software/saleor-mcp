from .channels import channels_router
from .checkout import checkout_router
from .customers import customers_router
from .orders import orders_router
from .products import products_router
from .promotions import promotions_router
from .utils import utils_router

__all__ = [
    "channels_router",
    "checkout_router",
    "customers_router",
    "orders_router",
    "products_router",
    "promotions_router",
    "utils_router",
]

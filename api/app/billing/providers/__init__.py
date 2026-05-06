"""Payment provider adapters — auto-register all providers on import."""

from app.billing.providers.paddle_provider import PaddleProvider  # noqa: F401
from app.billing.providers.paypal_provider import PayPalProvider  # noqa: F401
from app.billing.providers.square_provider import SquareProvider  # noqa: F401
from app.billing.providers.stripe_provider import StripeProvider  # noqa: F401

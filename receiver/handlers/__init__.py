
def register_handlers() -> None:
    """Import all handler modules to register their callbacks."""
    from . import conversations as _conversations  # noqa: F401
    from . import webhook_forwarder as _webhook_forwarder  # noqa: F401
    from . import logger as _logger  # noqa: F401

    # Export names for ``from handlers import *`` if desired
    globals().update(
        familiarize_conv_handler=_conversations.familiarize_conv_handler,
        forward_all_messages=_webhook_forwarder.forward_all_messages,
        log_message=_logger.log_message,
    )

__all__ = [
    "register_handlers",
    "familiarize_conv_handler",
    "forward_all_messages",
    "log_message",
]

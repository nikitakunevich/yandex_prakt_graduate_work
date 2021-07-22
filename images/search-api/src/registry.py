from contextvars import ContextVar

filter_premium = ContextVar("filter_premium", default=True)

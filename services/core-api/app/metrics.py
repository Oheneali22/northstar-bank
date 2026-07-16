from prometheus_client import Counter, Histogram

HTTP_REQUESTS = Counter(
    "northstar_http_requests_total",
    "Total HTTP requests",
    ("method", "path", "status"),
)
HTTP_DURATION = Histogram(
    "northstar_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ("method", "path"),
)
TRANSFERS = Counter(
    "northstar_transfers_total",
    "Transfer attempts by outcome",
    ("outcome",),
)
TRANSFER_AMOUNT = Histogram(
    "northstar_transfer_amount_cents",
    "Completed transfer amount in cents",
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000, 500000),
)

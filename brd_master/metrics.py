# metrics.py
from prometheus_client import Counter, Summary, REGISTRY

class MetricsSingleton:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MetricsSingleton, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            # Clear any existing metrics with these names
            collectors_to_remove = []
            for collector in REGISTRY._collector_to_names:
                for name in REGISTRY._collector_to_names[collector]:
                    if name in [
                        "request_processing_seconds",
                        "processed_pdfs_total",
                        "analyzed_pages_total",
                        "analysis_errors_total",
                        "analysis_duration_seconds"
                    ]:
                        collectors_to_remove.append(collector)
            
            for collector in collectors_to_remove:
                REGISTRY.unregister(collector)

            # Create new metrics
            self.request_time = Summary("request_processing_seconds", "Time spent processing request")
            self.processed_pdfs = Counter("processed_pdfs_total", "Total number of PDFs processed")
            self.analyzed_pages = Counter("analyzed_pages_total", "Total number of pages analyzed")
            self.analysis_errors = Counter("analysis_errors_total", "Total number of analysis errors")
            self.analysis_duration = Summary("analysis_duration_seconds", "Time spent analyzing each page")
            
            self._initialized = True

# Create global metrics instance
metrics = MetricsSingleton()

# Asynchronous context manager for timing
class AsyncTimer:
    def __init__(self, summary_metric):
        self._summary_metric = summary_metric

    async def __aenter__(self):
        import time
        self._start_time = time.time()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self._start_time
        self._summary_metric.observe(duration)
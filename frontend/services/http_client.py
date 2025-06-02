import requests
import asyncio
from services.tracing_service import TracingService

tracing_service = TracingService()

async def make_traced_request(url: str, method: str = "GET", **kwargs):
    return await tracing_service.trace_request(url, method, **kwargs)

def make_request(url: str, method: str = "GET", **kwargs):
    """Synchronous wrapper for traced requests"""
    return asyncio.run(make_traced_request(url, method, **kwargs)) 
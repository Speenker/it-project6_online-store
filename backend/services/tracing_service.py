import uuid
from datetime import datetime
from typing import Optional
import httpx
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import MutableHeaders

class TracingService:
    def __init__(self, clickhouse_url: str = "http://clickhouse:8123"):
        self.clickhouse_url = clickhouse_url

    async def create_trace(self, 
                          service_name: str,
                          request_path: str,
                          method: str,
                          status_code: int,
                          duration_ms: int,
                          trace_id: Optional[str] = None) -> str:
        if not trace_id:
            trace_id = str(uuid.uuid4())
            
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            
        query = f"""
        INSERT INTO traces (trace_id, service_name, timestamp, request_path, method, status_code, duration_ms)
        VALUES (
            '{trace_id}',
            '{service_name}',
            '{timestamp}',
            '{request_path}',
            '{method}',
            {status_code},
            {duration_ms}
        )
        """
        
        async with httpx.AsyncClient() as client:
            await client.post(self.clickhouse_url, data=query)
            
        return trace_id

class TracingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, tracing_service: TracingService):
        super().__init__(app)
        self.tracing_service = tracing_service

    async def dispatch(self, request: Request, call_next):
        start_time = datetime.utcnow()
        
        # Получаем trace_id из заголовков
        trace_id = request.headers.get("X-Trace-ID")
        if not trace_id:
            # Генерируем новый trace_id только если его нет в заголовках
            trace_id = str(uuid.uuid4())
        
        # Создаем новый scope с добавленным заголовком
        scope = dict(request.scope)
        headers = dict(scope["headers"])
        headers[b"x-trace-id"] = trace_id.encode()
        scope["headers"] = [(k, v) for k, v in headers.items()]
        
        # Создаем новый request с обновленным scope
        request = Request(scope)
        
        # Создаем новый response с добавленным заголовком
        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        await self.tracing_service.create_trace(
            service_name="backend",
            request_path=str(request.url.path),
            method=request.method,
            status_code=response.status_code,
            duration_ms=duration_ms,
            trace_id=trace_id
        )
        
        return response 
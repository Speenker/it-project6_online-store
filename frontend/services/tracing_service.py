import uuid
import httpx
from datetime import datetime
from typing import Optional
import streamlit as st

class TracingService:
    def __init__(self, clickhouse_url: str = "http://clickhouse:8123"):
        self.clickhouse_url = clickhouse_url

    def get_trace_id(self) -> str:
        if "trace_id" not in st.session_state:
            st.session_state.trace_id = str(uuid.uuid4())
        return st.session_state.trace_id

    def reset_trace_id(self):
        if "trace_id" in st.session_state:
            del st.session_state.trace_id

    async def create_trace(self,
                          service_name: str,
                          request_path: str,
                          method: str,
                          status_code: int,
                          duration_ms: int,
                          trace_id: Optional[str] = None) -> str:
        if not trace_id:
            trace_id = self.get_trace_id()

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

    async def trace_request(self, url: str, method: str = "GET", **kwargs) -> httpx.Response:
        start_time = datetime.utcnow()
        
        trace_id = self.get_trace_id()
        
        headers = kwargs.get("headers", {})
        headers["X-Trace-ID"] = trace_id
        kwargs["headers"] = headers
        
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, **kwargs)
            
            if "X-Trace-ID" in response.headers:
                new_trace_id = response.headers["X-Trace-ID"]
                if new_trace_id != st.session_state.trace_id:
                    st.session_state.trace_id = new_trace_id
                    
        duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        await self.create_trace(
            service_name="frontend",
            request_path=url,
            method=method,
            status_code=response.status_code,
            duration_ms=duration_ms,
            trace_id=trace_id
        )
        
        return response 
CREATE TABLE IF NOT EXISTS traces (
    trace_id UUID,
    service_name String,
    timestamp DateTime,
    request_path String,
    method String,
    status_code UInt16,
    duration_ms UInt32
) ENGINE = MergeTree()
ORDER BY (trace_id, timestamp); 
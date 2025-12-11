# Logging System Documentation

## Overview
Alpha Research API now includes a comprehensive logging system with:
- 📝 File-based logging with automatic rotation
- 🎨 Colored console output
- 🔍 Trace IDs for error tracking
- 📊 Log viewer API endpoint
- 🚨 Dedicated error logging

## Log Files

Logs are stored in the `/logs` directory:

| File | Purpose | Level | Rotation |
|------|---------|-------|----------|
| `api.log` | General API requests and responses | INFO | 10MB, 5 backups |
| `research.log` | Research paper operations (detailed) | DEBUG | 10MB, 5 backups |
| `errors.log` | Critical errors and exceptions | ERROR | 10MB, 10 backups |

## Viewing Logs

### Via API Endpoint

Access logs directly through the API:

```bash
# View recent API logs (last 100 lines)
curl http://localhost:8001/api/research/logs/api?lines=100

# View research operation logs
curl http://localhost:8001/api/research/logs/research?lines=50

# View error logs
curl http://localhost:8001/api/research/logs/errors?lines=200
```

Response format:
```json
{
  "log_type": "research",
  "log_file": "/path/to/logs/research.log",
  "lines_requested": 100,
  "lines_available": 87,
  "file_size_bytes": 45123,
  "last_modified": "2025-12-12T00:30:45.123456",
  "entries": [
    "2025-12-12 00:30:45 | INFO | alpha_research.research | Starting workflow...",
    "2025-12-12 00:30:46 | ERROR | alpha_research.research | Workflow failed..."
  ],
  "hint": "Use ?lines=N to get more/fewer lines (max 1000)"
}
```

### Via Terminal

```bash
# Tail API logs in real-time
tail -f logs/api.log

# View last 50 lines of research logs
tail -n 50 logs/research.log

# Search for errors
grep ERROR logs/errors.log

# View logs with color highlighting (recommended)
tail -f logs/api.log | bat --paging=never -l log
```

## Error Tracking with Trace IDs

Every error now includes a unique 8-character trace ID for easy debugging:

### Example Error Response

```json
{
  "detail": {
    "error": "Workflow failed with exit code 1",
    "trace_id": "a3b5c7d9",
    "exit_code": 1,
    "stderr": "Failed to connect to ArXiv API",
    "stdout": "Starting fetch...\nConnecting...",
    "suggestion": "Check logs/research.log for detailed error information"
  }
}
```

### Finding Errors by Trace ID

```bash
# Search all logs for specific trace ID
grep "a3b5c7d9" logs/*.log

# Search research logs
grep "\[a3b5c7d9\]" logs/research.log
```

## Log Format

All logs use a consistent format:

```
TIMESTAMP | LEVEL | LOGGER | FUNCTION:LINE | MESSAGE
```

Example:
```
2025-12-12 14:35:22 | INFO | api.main | log_requests:28 | → POST /api/research/wechat/generate | Client: 127.0.0.1
2025-12-12 14:35:23 | ERROR | alpha_research.errors | generate_research_paper:272 | [bd296c8e] Workflow failed
```

## Console Output Colors

Console logs are color-coded for easy reading:

- 🔵 **DEBUG**: Cyan
- 🟢 **INFO**: Green  
- 🟡 **WARNING**: Yellow
- 🔴 **ERROR**: Red
- 🟣 **CRITICAL**: Magenta

## Request Logging

All HTTP requests are automatically logged with:
- Method and path
- Client IP address
- Response status code
- Duration in milliseconds

Example:
```
2025-12-12 14:35:22 | INFO | api.main | → GET /api/market/quotes?symbols=AAPL | Client: 127.0.0.1
2025-12-12 14:35:22 | INFO | api.main | ← GET /api/market/quotes | Status: 200 | Duration: 45.23ms
```

## Research Paper Generation Logging

When generating research papers, detailed logging tracks:

1. **Start**: Workflow initiation with trace ID
2. **Script Path**: Verification of workflow script location
3. **Execution**: subprocess output (stdout/stderr)
4. **Errors**: Detailed error messages with suggestions
5. **Completion**: Success confirmation

Example:
```
2025-12-12 14:35:22 | INFO | alpha_research.research | [a3b5c7d9] Starting research paper generation workflow
2025-12-12 14:35:22 | INFO | alpha_research.research | [a3b5c7d9] Script path: /path/to/research-tracker/scripts/daily_workflow.sh
2025-12-12 14:35:22 | INFO | alpha_research.research | [a3b5c7d9] Executing workflow script (timeout: 300s)...
2025-12-12 14:35:45 | INFO | alpha_research.research | [a3b5c7d9] Workflow stdout: Fetched 10 papers from ArXiv...
2025-12-12 14:36:10 | INFO | alpha_research.research | [a3b5c7d9] Workflow completed successfully
```

## Error Scenarios

### 1. Workflow Script Not Found

**Error Response:**
```json
{
  "detail": {
    "error": "Workflow script not found at: /path/to/script.sh",
    "trace_id": "x7y8z9a1",
    "expected_path": "/path/to/research-tracker/scripts/daily_workflow.sh"
  }
}
```

**Log Entry:**
```
ERROR | alpha_research.errors | [x7y8z9a1] Workflow script not found at: /path/to/script.sh
```

### 2. Workflow Execution Failure

**Error Response:**
```json
{
  "detail": {
    "error": "Workflow failed with exit code 1",
    "trace_id": "b2c3d4e5",
    "exit_code": 1,
    "stderr": "Network connection timeout",
    "stdout": "Fetching papers...\nAttempting connection...",
    "suggestion": "Check logs/research.log for detailed error information"
  }
}
```

**Log Entry:**
```
ERROR | alpha_research.errors | [b2c3d4e5] Workflow failed with exit code 1
stdout: Fetching papers...
stderr: Network connection timeout
```

### 3. Timeout

**Error Response:**
```json
{
  "detail": {
    "error": "Workflow timeout (exceeded 5 minutes)",
    "trace_id": "f6g7h8i9",
    "timeout_seconds": 300,
    "suggestion": "The research workflow is taking too long. Check if ArXiv API is slow or if there are network issues."
  }
}
```

## Log Rotation

Logs automatically rotate when they reach 10MB:
- `api.log` → `api.log.1` → `api.log.2` → ... → `api.log.5`
- Keeps 5 backup files (50MB total per log type)
- Error logs keep 10 backups (100MB total)

## Programmatic Logging

To add logging to new modules:

```python
from api.logging_config import get_logger

# At module level
logger = get_logger(__name__)

# In functions
logger.debug("Detailed debugging information")
logger.info("Normal operational message")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical system error")
```

### With Exception Tracebacks

```python
from api.logging_config import error_logger
import traceback

try:
    risky_operation()
except Exception as e:
    error_logger.error(
        f"Operation failed: {str(e)}\n"
        f"Traceback:\n{traceback.format_exc()}"
    )
```

## Monitoring in Production

### Real-time Monitoring

```bash
# Watch all API activity
tail -f logs/api.log

# Monitor errors only
tail -f logs/errors.log | grep ERROR

# Watch research operations
tail -f logs/research.log | grep -E "Starting|completed|failed"
```

### Log Analysis

```bash
# Count errors in last hour
grep "$(date -v-1H '+%Y-%m-%d %H')" logs/errors.log | wc -l

# Find slowest requests (>1000ms)
grep "Duration:" logs/api.log | awk -F'Duration: ' '{print $2}' | awk -F'ms' '{if($1>1000) print}'

# Most common errors
grep ERROR logs/errors.log | cut -d'|' -f5 | sort | uniq -c | sort -rn | head -10
```

## Debugging Workflow

When you see an error:

1. **Copy the trace ID** from the error response
2. **Search logs**: `grep "trace_id_here" logs/*.log`
3. **View context**: Read lines before/after the trace ID
4. **Check research.log**: Most detailed workflow information
5. **Use log viewer API** for programmatic access

## API Reference

### GET /api/research/logs/{log_type}

View application logs through the API.

**Parameters:**
- `log_type` (path): Type of log (`api`, `research`, `errors`)
- `lines` (query, optional): Number of lines to return (default: 100, max: 1000)

**Response:**
```typescript
{
  log_type: string;
  log_file: string;
  lines_requested: number;
  lines_available: number;
  file_size_bytes: number;
  last_modified: string; // ISO 8601
  entries: string[];
  hint: string;
}
```

**Examples:**
```bash
GET /api/research/logs/api
GET /api/research/logs/research?lines=500
GET /api/research/logs/errors?lines=50
```

## Best Practices

1. ✅ Always include trace IDs in error reports
2. ✅ Use log viewer API for automated monitoring
3. ✅ Check `research.log` for workflow details
4. ✅ Monitor `errors.log` for critical issues
5. ✅ Keep logs directory under 500MB (automatic rotation helps)
6. ✅ Use `grep` with trace IDs for quick debugging
7. ✅ Archive old logs before deployment

## Troubleshooting

### Logs not appearing

**Check:**
1. Permissions: `ls -la logs/`
2. Disk space: `df -h`
3. Log level: Default is INFO, DEBUG needs configuration

### Log files too large

**Solution:**
1. Automatic rotation happens at 10MB
2. Manually rotate: `mv logs/api.log logs/api.log.old`
3. Clean old backups: `rm logs/*.log.[6-9]`

### Can't access log viewer endpoint

**Check:**
1. API is running: `curl http://localhost:8001/`
2. Endpoint path: `/api/research/logs/{type}`
3. Valid log type: `api`, `research`, or `errors`

---

**Questions or Issues?**  
Check the main [README.md](../README.md) or open a GitHub issue with the trace ID from your error.

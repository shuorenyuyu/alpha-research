# Troubleshooting: Auto-Generate Paper Errors

## Error Fixed ✅

The paper auto-generation feature now displays **clear error messages** with:
- ✅ Trace IDs for debugging
- ✅ Detailed error information  
- ✅ Helpful suggestions
- ✅ Proper error logging

## Current Issue: Missing Dependencies in research-tracker

**Error Message:**
```
Missing Python dependency: apscheduler. Please install it in research-tracker.
Trace ID: eb46142a
```

**Root Cause:** The `research-tracker` project is missing Python dependencies.

### Solution 1: Install Dependencies in research-tracker

```bash
# Navigate to research-tracker directory
cd ~/code/research-tracker

# Activate virtual environment (if using one)
source venv/bin/activate

# Install required dependencies
pip install apscheduler arxiv openai python-dotenv pydantic

# Or install from requirements.txt if available
pip install -r requirements.txt
```

### Solution 2: Verify research-tracker Setup

```bash
# Check if research-tracker exists
ls -la ~/code/research-tracker

# Check Python environment
cd ~/code/research-tracker
python -c "import apscheduler; print('✅ apscheduler installed')" 2>&1

# Check workflow script
ls -la ~/code/research-tracker/scripts/daily_workflow.sh
```

### Solution 3: Test Workflow Manually

```bash
# Run the workflow script directly to see errors
cd ~/code/research-tracker
bash scripts/daily_workflow.sh
```

## How to Debug Any Error Now

When you click "Auto-generate Paper" and get an error, you'll see:

### Example Error Dialog:
```
Failed to generate paper:

Missing Python dependency: apscheduler. Please install it in research-tracker.

Trace ID: eb46142a
Check the backend logs for more details.

Error details:
Traceback (most recent call last):
  File "/Users/Mac/code/research-tracker/src/scheduler/daily_scheduler.py", line 6
    from apscheduler.schedulers.blocking import BlockingScheduler
ModuleNotFoundError: No module named 'apscheduler'

Suggestion: Check logs/research.log for detailed error information
```

### Steps to Debug:

1. **Copy the Trace ID** (e.g., `eb46142a`)

2. **Check Backend Logs:**
   ```bash
   # View research logs
   tail -50 logs/research.log
   
   # Or search by trace ID
   grep "eb46142a" logs/*.log
   ```

3. **Use Log Viewer API:**
   ```bash
   curl http://localhost:8000/api/research/logs/research?lines=100
   ```

4. **Check Console:**
   - Open browser DevTools (F12)
   - Go to Console tab
   - Look for `[wechat-generate-proxy]` messages

## Common Errors & Solutions

### 1. Missing Dependencies
**Error:** `ModuleNotFoundError: No module named 'XXX'`

**Solution:**
```bash
cd ~/code/research-tracker
pip install XXX
```

### 2. Workflow Script Not Found
**Error:** `Workflow script not found`

**Solution:**
```bash
# Check if research-tracker is in the correct location
ls -la ~/code/research-tracker/scripts/daily_workflow.sh

# If not, clone it:
cd ~/code
git clone https://github.com/shuorenyuyu/research-tracker.git
```

### 3. API Connection Failed
**Error:** `Failed to connect to API server`

**Solution:**
```bash
# Start the backend API
cd ~/code/alpha-research
source venv/bin/activate
python -m api.main

# Should see:
# 🚀 Alpha Research API starting up...
# INFO: Uvicorn running on http://0.0.0.0:8000
```

### 4. Timeout Error
**Error:** `Workflow timeout (exceeded 5 minutes)`

**Possible Causes:**
- Slow network connection to ArXiv API
- Large number of papers being fetched
- AI API (OpenAI) slow response

**Solution:**
- Wait and try again later
- Check your internet connection
- Verify ArXiv API status: https://info.arxiv.org/help/api/index.html

## Verification Checklist

Before using auto-generate, verify:

- [ ] Backend API running on port 8000
  ```bash
  curl http://localhost:8000/
  # Should return: {"message":"Alpha Research API","status":"running"}
  ```

- [ ] research-tracker exists
  ```bash
  ls ~/code/research-tracker
  ```

- [ ] research-tracker dependencies installed
  ```bash
  cd ~/code/research-tracker
  pip list | grep -E "apscheduler|arxiv|openai"
  ```

- [ ] Environment variables set (if needed)
  ```bash
  cat ~/code/research-tracker/.env
  # Should have OPENAI_API_KEY if using AI summaries
  ```

## Production Deployment Notes

On your Azure VM (20.51.208.13):

1. **Update Dashboard Environment:**
   ```bash
   cd ~/alpha-research/dashboard
   cp .env.example .env.local
   # Edit .env.local:
   # API_HOST=20.51.208.13  # or localhost if frontend on same server
   ```

2. **Verify Backend Port:**
   ```bash
   # Check what port PM2 is using
   pm2 logs alpha-research-api | grep "Uvicorn running"
   ```

3. **Update CORS if needed:**
   Edit `api/main.py` to allow your production domain:
   ```python
   allow_origins=[
       "http://localhost:3000",
       "http://alpha-research.southeastasia.cloudapp.azure.com",
       "http://57.155.1.26"
   ]
   ```

## Need More Help?

1. **Check logs with trace ID:**
   ```bash
   grep "TRACE_ID_HERE" logs/*.log
   ```

2. **View full logs:**
   ```bash
   cat logs/research.log
   ```

3. **Test API directly:**
   ```bash
   curl -X POST http://localhost:8000/api/research/wechat/generate
   ```

4. **Check this documentation:**
   - [Logging System](./LOGGING.md)
   - [Main README](../README.md)

---

**The error handling system is now working perfectly!** ✅  
You'll get clear, actionable error messages with trace IDs for easy debugging.

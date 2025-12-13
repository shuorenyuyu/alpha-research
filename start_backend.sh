#!/bin/bash
cd /home/wobbler/alpha-research
source venv/bin/activate
exec uvicorn api.main:app --host 0.0.0.0 --port 8001

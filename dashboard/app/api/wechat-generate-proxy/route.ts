import { NextResponse } from 'next/server';

export async function POST() {
  const apiHost = process.env.API_HOST || 'localhost';
  const apiPort = process.env.API_PORT || '8000';
  const apiUrl = `http://${apiHost}:${apiPort}/api/research/wechat/generate`;
  
  console.log(`[wechat-generate-proxy] Calling API: ${apiUrl}`);
  
  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const error = await response.json();
      console.error('[wechat-generate-proxy] API error:', error);
      
      // Extract better error message from the structured error response
      let errorMessage = 'Failed to generate paper';
      
      if (error.detail) {
        if (typeof error.detail === 'object') {
          // New structured error format with trace_id
          errorMessage = error.detail.error || errorMessage;
          const traceId = error.detail.trace_id;
          const stderr = error.detail.stderr;
          
          // Create detailed error for user
          if (stderr && stderr.includes('ModuleNotFoundError')) {
            const moduleName = stderr.match(/No module named '(\w+)'/)?.[1];
            errorMessage = `Missing Python dependency: ${moduleName}. Please install it in research-tracker.`;
          } else if (traceId) {
            errorMessage += ` (Trace ID: ${traceId})`;
          }
        } else {
          errorMessage = error.detail;
        }
      }
      
      return NextResponse.json(
        { 
          error: errorMessage,
          detail: error.detail,
          status: response.status 
        },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log('[wechat-generate-proxy] Success:', data);
    return NextResponse.json(data);
  } catch (error) {
    console.error('[wechat-generate-proxy] Request error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to API server. Please ensure the backend is running.' },
      { status: 500 }
    );
  }
}

import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const apiHost = process.env.API_HOST || 'localhost';
  const apiPort = process.env.API_PORT || '8000';
  const apiUrl = `http://${apiHost}:${apiPort}/api/research/search/theme`;
  
  console.log(`[theme-search-proxy] Calling API: ${apiUrl}`);
  
  try {
    const body = await request.json();
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body)
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      console.error('[theme-search-proxy] API error:', data);
    }
    
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error('[theme-search-proxy] Request error:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to connect to backend API',
        detail: String(error)
      },
      { status: 500 }
    );
  }
}

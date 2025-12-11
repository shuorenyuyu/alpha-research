import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  const apiHost = process.env.API_HOST || 'localhost';
  const apiUrl = `http://${apiHost}:8001/api/research/wechat/create`;
  
  try {
    const body = await request.json();
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    if (!response.ok) {
      const error = await response.json();
      return NextResponse.json(
        { error: error.detail || 'Failed to create article' },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error creating article:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

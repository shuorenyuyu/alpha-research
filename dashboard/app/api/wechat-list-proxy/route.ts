import { NextResponse } from 'next/server';

export async function GET() {
  const apiHost = process.env.API_HOST || 'localhost';
  const apiUrl = `http://${apiHost}:8001/api/research/wechat/list`;
  
  try {
    const response = await fetch(apiUrl, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch WeChat articles list' },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching WeChat articles list:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

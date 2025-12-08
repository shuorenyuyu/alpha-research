import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const filename = searchParams.get('filename');
  
  if (!filename) {
    return NextResponse.json(
      { error: 'Filename parameter is required' },
      { status: 400 }
    );
  }

  const apiHost = process.env.API_HOST || 'localhost';
  const apiUrl = `http://${apiHost}:8001/api/research/wechat/${filename}`;
  
  try {
    const response = await fetch(apiUrl);
    
    if (!response.ok) {
      return new NextResponse(
        'Article not found',
        { status: response.status }
      );
    }
    
    const html = await response.text();
    return new NextResponse(html, {
      headers: {
        'Content-Type': 'text/html',
      },
    });
  } catch (error) {
    console.error('Error fetching WeChat article:', error);
    return new NextResponse(
      'Internal server error',
      { status: 500 }
    );
  }
}

import { NextResponse } from 'next/server';

export async function DELETE(request: Request) {
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
    const response = await fetch(apiUrl, {
      method: 'DELETE'
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to delete article' },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error deleting article:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

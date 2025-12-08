import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const symbols = searchParams.get('symbols') || 'NVDA,MSFT,GOOGL,TSLA,AAPL';
  
  // In production, use the server hostname; in development, use localhost
  const apiHost = process.env.API_HOST || 'localhost';
  const apiUrl = `http://${apiHost}:8001/api/market/quotes?symbols=${symbols}`;
  
  try {
    const response = await fetch(apiUrl, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch market data' },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching market data:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

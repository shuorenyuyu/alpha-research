"use client";

import { useState, useEffect } from "react";

interface StockData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

export default function StocksPage() {
  const [stocks, setStocks] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mock stock data - replace with API call later
    const mockStocks: StockData[] = [
      { symbol: "NVDA", name: "NVIDIA", price: 135.50, change: 2.75, changePercent: 2.07 },
      { symbol: "MSFT", name: "Microsoft", price: 425.80, change: -1.20, changePercent: -0.28 },
      { symbol: "GOOGL", name: "Alphabet", price: 175.30, change: 3.50, changePercent: 2.04 },
      { symbol: "TSLA", name: "Tesla", price: 248.90, change: 5.60, changePercent: 2.30 },
      { symbol: "AAPL", name: "Apple", price: 195.20, change: -0.80, changePercent: -0.41 },
    ];
    
    setTimeout(() => {
      setStocks(mockStocks);
      setLoading(false);
    }, 500);
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading stock data...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="text-4xl font-bold text-gray-900 mb-8">Stock Market Dashboard</h1>
      
      {/* Market Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm text-gray-600 mb-2">Total Portfolio Value</h3>
          <p className="text-3xl font-bold text-gray-900">$125,450</p>
          <p className="text-sm text-green-600 mt-1">+$2,340 (1.9%)</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm text-gray-600 mb-2">Today's Gain/Loss</h3>
          <p className="text-3xl font-bold text-green-600">+$1,250</p>
          <p className="text-sm text-gray-600 mt-1">+1.0% today</p>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm text-gray-600 mb-2">Tracked Stocks</h3>
          <p className="text-3xl font-bold text-gray-900">{stocks.length}</p>
          <p className="text-sm text-gray-600 mt-1">Active positions</p>
        </div>
      </div>

      {/* Stock List */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Symbol
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Price
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Change
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Change %
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {stocks.map((stock) => (
              <tr key={stock.symbol} className="hover:bg-gray-50 cursor-pointer">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{stock.symbol}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{stock.name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">${stock.price.toFixed(2)}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className={`text-sm ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    stock.changePercent >= 0 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Chart Placeholder */}
      <div className="mt-8 bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Price Chart</h2>
        <div className="h-64 bg-gray-100 rounded flex items-center justify-center">
          <p className="text-gray-500">Interactive chart coming soon</p>
        </div>
      </div>
    </div>
  );
}

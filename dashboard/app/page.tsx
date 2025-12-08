"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function Home() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black overflow-hidden">
      {/* Animated background gradient */}
      <div
        className="absolute inset-0 opacity-30"
        style={{
          background: `radial-gradient(circle 600px at ${mousePosition.x}px ${mousePosition.y}px, rgba(59, 130, 246, 0.15), transparent)`,
        }}
      />

      {/* Main content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4">
        {/* Hero section */}
        <div className="text-center max-w-5xl mx-auto space-y-8">
          <h1 className="text-7xl md:text-8xl font-bold">
            <span className="bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent animate-gradient">
              Alpha Research
            </span>
          </h1>
          
          <p className="text-2xl md:text-3xl text-gray-300 font-light">
            AI-Powered Quantitative Investing Platform
          </p>
          
          <p className="text-lg text-gray-400 max-w-2xl mx-auto leading-relaxed">
            Combining cutting-edge artificial intelligence with quantitative analysis 
            to uncover market insights and drive data-driven investment decisions.
          </p>

          {/* Feature cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
            <Link href="/dashboard">
              <div className="group bg-gray-800/30 backdrop-blur-sm border border-gray-700 rounded-xl p-8 hover:border-blue-500 hover:bg-gray-800/50 transition-all cursor-pointer">
                <div className="text-5xl mb-4">📊</div>
                <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-blue-400 transition-colors">
                  Dashboard
                </h3>
                <p className="text-gray-400">
                  Real-time market data and analytics with live metrics from Yahoo Finance
                </p>
              </div>
            </Link>

            <Link href="/research">
              <div className="group bg-gray-800/30 backdrop-blur-sm border border-gray-700 rounded-xl p-8 hover:border-purple-500 hover:bg-gray-800/50 transition-all cursor-pointer">
                <div className="text-5xl mb-4">📚</div>
                <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-purple-400 transition-colors">
                  Research
                </h3>
                <p className="text-gray-400">
                  Curated research papers and insights on AI, ML, and quantitative finance
                </p>
              </div>
            </Link>

            <div className="group bg-gray-800/30 backdrop-blur-sm border border-gray-700 rounded-xl p-8 hover:border-pink-500 hover:bg-gray-800/50 transition-all">
              <div className="text-5xl mb-4">🤖</div>
              <h3 className="text-2xl font-bold text-white mb-3 group-hover:text-pink-400 transition-colors">
                AI Models
              </h3>
              <p className="text-gray-400">
                Advanced machine learning models for market prediction and analysis
              </p>
              <span className="inline-block mt-3 text-sm text-gray-500 italic">Coming Soon</span>
            </div>
          </div>

          {/* Stats section */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16 pt-12 border-t border-gray-800">
            <div className="text-center">
              <div className="text-4xl font-bold text-blue-400">5+</div>
              <div className="text-gray-400 mt-2">Stock Tracked</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-400">Real-time</div>
              <div className="text-gray-400 mt-2">Market Data</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-pink-400">24/7</div>
              <div className="text-gray-400 mt-2">Analysis</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-400">Auto</div>
              <div className="text-gray-400 mt-2">Refresh</div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="absolute bottom-8 text-center text-gray-500 text-sm">
          <p>Powered by AI • Built with Next.js & FastAPI</p>
        </div>
      </div>
    </div>
  );
}

interface StockData {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

export default function Home() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [stocks, setStocks] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(true);
  const [portfolioValue, setPortfolioValue] = useState(0);
  const [todayGain, setTodayGain] = useState(0);
  const [todayGainPercent, setTodayGainPercent] = useState(0);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener("mousemove", handleMouseMove);

    // Fetch real stock data
    const fetchStocks = async () => {
      try {
        const response = await fetch('/api/market-proxy?symbols=NVDA,MSFT,GOOGL,TSLA,AAPL');
        if (response.ok) {
          const data = await response.json();
          const stockData = data.map((stock: any) => ({
            symbol: stock.symbol,
            name: stock.name,
            price: stock.price,
            change: stock.change,
            changePercent: stock.changePercent // API uses camelCase
          }));
          setStocks(stockData);
          
          // Calculate portfolio stats (assuming 10 shares each)
          const sharesPerStock = 10;
          const totalValue = stockData.reduce((sum: number, stock: StockData) => sum + (stock.price * sharesPerStock), 0);
          const totalGain = stockData.reduce((sum: number, stock: StockData) => sum + (stock.change * sharesPerStock), 0);
          const gainPercent = (totalGain / (totalValue - totalGain)) * 100;
          
          setPortfolioValue(totalValue);
          setTodayGain(totalGain);
          setTodayGainPercent(gainPercent);
        }
      } catch (error) {
        console.error('Error fetching stocks:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStocks();

    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white overflow-hidden relative pt-4">
      {/* Animated gradient following mouse */}
      <div 
        className="fixed pointer-events-none inset-0 z-0"
        style={{
          background: `radial-gradient(600px circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(59, 130, 246, 0.15), transparent 40%)`,
        }}
      />
      
      {/* Background grid */}
      <div className="fixed inset-0 z-0" style={{
        backgroundImage: `linear-gradient(rgba(59, 130, 246, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(59, 130, 246, 0.05) 1px, transparent 1px)`,
        backgroundSize: '50px 50px'
      }} />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16 pt-8">
          <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            Alpha Research
          </h1>
          <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
            AI-powered investment research platform combining cutting-edge research insights with quantitative market analysis
          </p>
          <div className="flex gap-4 justify-center">
            <Link 
              href="/research"
              className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg font-semibold hover:from-blue-500 hover:to-purple-500 transition-all transform hover:scale-105"
            >
              Explore Research
            </Link>
          </div>
        </div>

        {/* Market Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6 hover:border-blue-500 transition-all transform hover:scale-105">
            <h3 className="text-sm text-gray-400 mb-2">Total Portfolio Value</h3>
            <p className="text-3xl font-bold text-white">${portfolioValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</p>
            <p className={`text-sm mt-1 ${todayGain >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {todayGain >= 0 ? '+' : ''}${Math.abs(todayGain).toFixed(2)} ({todayGainPercent >= 0 ? '+' : ''}{todayGainPercent.toFixed(2)}%)
            </p>
          </div>
          
          <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6 hover:border-purple-500 transition-all transform hover:scale-105">
            <h3 className="text-sm text-gray-400 mb-2">Today's Gain/Loss</h3>
            <p className={`text-3xl font-bold ${todayGain >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {todayGain >= 0 ? '+' : ''}${Math.abs(todayGain).toFixed(2)}
            </p>
            <p className="text-sm text-gray-400 mt-1">
              {todayGainPercent >= 0 ? '+' : ''}{todayGainPercent.toFixed(2)}% today
            </p>
          </div>
          
          <div className="bg-gradient-to-br from-gray-900 to-gray-800 border border-gray-700 rounded-lg p-6 hover:border-pink-500 transition-all transform hover:scale-105">
            <h3 className="text-sm text-gray-400 mb-2">Active Positions</h3>
            <p className="text-3xl font-bold text-white">{stocks.length}</p>
            <p className="text-sm text-gray-400 mt-1">Tracked stocks</p>
          </div>
        </div>

        {/* Stock Market Dashboard */}
        <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-lg overflow-hidden mb-12">
          <div className="p-6 border-b border-gray-700">
            <h2 className="text-2xl font-bold text-white">Market Overview</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-700">
              <thead className="bg-gray-800/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Symbol</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Company</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Price</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Change</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Change %</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {stocks.map((stock) => (
                  <tr key={stock.symbol} className="hover:bg-gray-800/50 cursor-pointer transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-white">{stock.symbol}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-300">{stock.name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-white">${stock.price.toFixed(2)}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`text-sm ${stock.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        stock.changePercent >= 0 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                      }`}>
                        {stock.changePercent >= 0 ? '+' : ''}{stock.changePercent.toFixed(2)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8">
          <div className="group bg-gradient-to-br from-blue-900/20 to-blue-800/20 border border-blue-700/50 rounded-lg p-8 hover:border-blue-500 transition-all transform hover:scale-105">
            <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">🤖</div>
            <h3 className="text-xl font-semibold mb-2 text-white">AI-Powered Analysis</h3>
            <p className="text-gray-400">GPT-4 generated summaries with investment insights from cutting-edge research papers</p>
          </div>

          <div className="group bg-gradient-to-br from-purple-900/20 to-purple-800/20 border border-purple-700/50 rounded-lg p-8 hover:border-purple-500 transition-all transform hover:scale-105">
            <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">📈</div>
            <h3 className="text-xl font-semibold mb-2 text-white">Quantitative Strategies</h3>
            <p className="text-gray-400">Backtested trading strategies and multi-factor models for systematic investing</p>
          </div>

          <div className="group bg-gradient-to-br from-pink-900/20 to-pink-800/20 border border-pink-700/50 rounded-lg p-8 hover:border-pink-500 transition-all transform hover:scale-105">
            <div className="text-4xl mb-4 group-hover:scale-110 transition-transform">🌏</div>
            <h3 className="text-xl font-semibold mb-2 text-white">Bilingual Content</h3>
            <p className="text-gray-400">English and Chinese research summaries for global investors and researchers</p>
          </div>
        </div>
      </div>
    </div>
  );
}

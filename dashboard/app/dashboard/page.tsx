"use client";

import { useState, useEffect } from "react";
import LivePortfolioToggle from "@/components/LivePortfolioToggle";

type StrategyType = "warren-buffett" | "li-lu" | "duan-yongping" | "market-cap-screener";

interface HoldingData {
  symbol: string;
  name: string;
  buy_date?: string;
  buy_price?: number;
  current_price: number;
  weight?: number;
  allocation?: number;
  gain_loss?: number;
  return_pct?: number;
  multiple?: number;
  holding_period_years?: number;
  notes?: string;
  // For Buffett-Munger
  pe_ratio?: number;
  roe?: number;
  market_cap?: number;
}

interface PortfolioData {
  stocks: HoldingData[];
  total_stocks: number;
  strategy: string;
  description?: string;
  // Buffett-Munger specific
  last_rebalance?: string;
  next_rebalance?: string;
  days_until_rebalance?: number;
  avg_pe?: number;
  avg_roe?: number;
  allocation_per_stock?: number;
  // Li Lu / Duan Yongping specific
  weighted_avg_return?: number;
  avg_holding_years?: number;
  winners?: number;
  losers?: number;
  best_performer?: {
    symbol: string;
    return: number;
    multiple: number;
  };
  philosophy?: string;
}

export default function DashboardPage() {
  const [activeStrategy, setActiveStrategy] = useState<StrategyType>("warren-buffett");
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPortfolio = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetch(`/api/portfolio/${activeStrategy}`);
        
        if (response.ok) {
          const data: PortfolioData = await response.json();
          setPortfolio(data);
        } else {
          setError(`Failed to fetch ${activeStrategy} portfolio`);
        }
      } catch (err) {
        setError('Error loading portfolio');
        console.error('Error fetching portfolio:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolio();
  }, [activeStrategy]);

  const strategyTabs = [
    { id: "warren-buffett" as StrategyType, name: "Warren Buffett", icon: "🐐" },
    { id: "li-lu" as StrategyType, name: "Li Lu 李录", icon: "🏔️" },
    { id: "duan-yongping" as StrategyType, name: "Duan Yongping 段永平", icon: "🍎" },
    { id: "market-cap-screener" as StrategyType, name: "Market Cap Top 25", icon: "🎯" },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-black to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading portfolio...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-black to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-2xl text-red-400">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black to-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Investment Portfolios</h1>
          <p className="text-gray-400">Track legendary investors' strategies and holdings</p>
        </div>

        {/* Strategy Tabs */}
        <div className="flex space-x-4 mb-8 border-b border-gray-700">
          {strategyTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveStrategy(tab.id)}
              className={`px-6 py-3 font-semibold transition-all ${
                activeStrategy === tab.id
                  ? "text-blue-400 border-b-2 border-blue-400"
                  : "text-gray-400 hover:text-gray-300"
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.name}
            </button>
          ))}
        </div>

        {/* Portfolio Content */}
        {portfolio && (
          <>
            {/* Strategy Header */}
            <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl p-6 mb-6 border border-gray-700">
              <h2 className="text-2xl font-bold mb-2">{portfolio.strategy}</h2>
              <p className="text-gray-400">{portfolio.description || portfolio.philosophy}</p>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <MetricCard
                title="Total Holdings"
                value={portfolio.total_stocks.toString()}
                icon="📊"
              />
              
              {activeStrategy === "market-cap-screener" && portfolio.avg_pe && (
                <>
                  <MetricCard
                    title="Avg P/E Ratio"
                    value={portfolio.avg_pe.toFixed(2)}
                    icon="💰"
                  />
                  <MetricCard
                    title="Avg ROE"
                    value={`${portfolio.avg_roe?.toFixed(2)}%`}
                    icon="📈"
                  />
                  <MetricCard
                    title="Next Rebalance"
                    value={`${portfolio.days_until_rebalance} days`}
                    icon="📅"
                  />
                </>
              )}
              
              {(activeStrategy === "warren-buffett" || activeStrategy === "li-lu" || activeStrategy === "duan-yongping") && (
                <>
                  <MetricCard
                    title="Avg Return"
                    value={`${portfolio.weighted_avg_return?.toFixed(1)}%`}
                    icon="💎"
                    isPositive={(portfolio.weighted_avg_return || 0) > 0}
                  />
                  <MetricCard
                    title="Avg Holding"
                    value={`${portfolio.avg_holding_years?.toFixed(1)} years`}
                    icon="⏳"
                  />
                  <MetricCard
                    title="Win Rate"
                    value={`${portfolio.winners}/${portfolio.total_stocks}`}
                    icon="🎯"
                  />
                </>
              )}
            </div>

            {/* Live Portfolio Toggle for Warren Buffett and Li Lu */}
            {(activeStrategy === "warren-buffett" || activeStrategy === "li-lu") ? (
              <LivePortfolioToggle 
                investor={activeStrategy}
                historicalData={{
                  stocks: portfolio.stocks as any,
                  weighted_avg_return: portfolio.weighted_avg_return || 0,
                  avg_holding_years: portfolio.avg_holding_years || 0,
                  winners: portfolio.winners || 0,
                  losers: portfolio.losers || 0,
                  best_performer: portfolio.best_performer
                }}
              />
            ) : (
              <>
                {/* Holdings Table for other strategies (Market Cap and Duan Yongping) */}
                <div className="bg-gray-900 rounded-xl border border-gray-700 overflow-hidden">
                  <div className="p-6">
                    <h3 className="text-xl font-semibold mb-4">Holdings</h3>
                
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-700 text-left">
                        <th className="pb-3 px-4">Symbol</th>
                        <th className="pb-3 px-4">Company</th>
                        {activeStrategy === "duan-yongping" && (
                          <>
                            <th className="pb-3 px-4 text-right">Buy Date</th>
                            <th className="pb-3 px-4 text-right">Buy Price</th>
                          </>
                        )}
                        <th className="pb-3 px-4 text-right">Current Price</th>
                        <th className="pb-3 px-4 text-right">Weight</th>
                        {activeStrategy === "duan-yongping" && (
                          <>
                            <th className="pb-3 px-4 text-right">Return</th>
                            <th className="pb-3 px-4 text-right">Multiple</th>
                            <th className="pb-3 px-4 text-right">Years</th>
                          </>
                        )}
                      </tr>
                    </thead>
                    <tbody>
                      {portfolio.stocks.map((stock, index) => (
                        <tr
                          key={stock.symbol}
                          className={`border-b border-gray-800 hover:bg-gray-800 transition ${
                            index < 10 ? "" : "hidden md:table-row"
                          }`}
                        >
                          <td className="py-4 px-4">
                            <span className="font-mono font-semibold text-blue-400">
                              {stock.symbol}
                            </span>
                          </td>
                          <td className="py-4 px-4 text-gray-300">{stock.name}</td>
                          
                          {activeStrategy === "duan-yongping" && (
                            <>
                              <td className="py-4 px-4 text-right text-gray-400 text-sm">
                                {stock.buy_date}
                              </td>
                              <td className="py-4 px-4 text-right text-gray-400">
                                ${stock.buy_price?.toFixed(2)}
                              </td>
                            </>
                          )}
                          
                          <td className="py-4 px-4 text-right font-semibold">
                            ${stock.current_price.toFixed(2)}
                          </td>
                          
                          <td className="py-4 px-4 text-right">
                            <span className="px-2 py-1 bg-blue-900 text-blue-300 rounded text-sm">
                              {stock.weight ? stock.weight : `${stock.allocation?.toFixed(1)}%`}
                            </span>
                          </td>
                          
                          {activeStrategy === "duan-yongping" && (
                            <>
                              <td className="py-4 px-4 text-right">
                                <span className={stock.return_pct && stock.return_pct > 0 ? "text-green-400" : "text-red-400"}>
                                  {stock.return_pct?.toFixed(1)}%
                                </span>
                              </td>
                              
                              <td className="py-4 px-4 text-right font-semibold text-green-400">
                                {stock.multiple?.toFixed(1)}x
                              </td>
                              
                              <td className="py-4 px-4 text-right text-gray-400 text-sm">
                                {stock.holding_period_years?.toFixed(1)}
                              </td>
                            </>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* Best Performer Card (for Duan Yongping only, Buffett/Li Lu shown in toggle) */}
            {portfolio.best_performer && activeStrategy === "duan-yongping" && (
              <div className="mt-6 bg-gradient-to-r from-green-900 to-green-800 rounded-xl p-6 border border-green-700">
                <h3 className="text-xl font-semibold mb-2">🏆 Best Performer</h3>
                <p className="text-2xl font-bold">
                  {portfolio.best_performer.symbol} - {portfolio.best_performer.return.toFixed(1)}% 
                  ({portfolio.best_performer.multiple.toFixed(1)}x)
                </p>
              </div>
            )}
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function MetricCard({ 
  title, 
  value, 
  icon, 
  isPositive 
}: { 
  title: string; 
  value: string; 
  icon: string; 
  isPositive?: boolean;
}) {
  return (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm">{title}</span>
        <span className="text-2xl">{icon}</span>
      </div>
      <div className={`text-2xl font-bold ${
        isPositive !== undefined 
          ? isPositive ? "text-green-400" : "text-red-400"
          : "text-white"
      }`}>
        {value}
      </div>
    </div>
  );
}

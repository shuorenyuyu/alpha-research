"use client";

import { useState, useEffect } from "react";

interface LiveHolding {
  ticker: string;
  name: string;
  shares: number;
  value_millions: number;
  weight_pct: number;
  value_usd: number;
}

interface LivePortfolioData {
  investor: string;
  report_date: string;
  data_source: string;
  total_holdings: number;
  total_value_usd: number;
  total_value_millions: number;
  holdings: LiveHolding[];
  note?: string;
}

interface HistoricalHolding {
  symbol: string;
  name: string;
  buy_date: string;
  buy_price: number;
  current_price: number;
  return_pct: number;
  multiple?: number;
  holding_period_years: number;
}

interface Props {
  investor: "warren-buffett" | "li-lu";
  historicalData: {
    stocks: HistoricalHolding[];
    weighted_avg_return: number;
    avg_holding_years: number;
    winners: number;
    losers: number;
    best_performer?: {
      symbol: string;
      return: number;
      multiple: number;
    };
  };
}

export default function LivePortfolioToggle({ investor, historicalData }: Props) {
  const [viewMode, setViewMode] = useState<"historical" | "live">("historical");
  const [liveData, setLiveData] = useState<LivePortfolioData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (viewMode === "live" && !liveData) {
      fetchLiveData();
    }
  }, [viewMode]);

  const fetchLiveData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/live-portfolio/${investor}`);

      if (response.ok) {
        const data: LivePortfolioData = await response.json();
        setLiveData(data);
      } else {
        setError(`Failed to fetch live portfolio`);
      }
    } catch (err) {
      setError("Error loading live portfolio");
      console.error("Error fetching live portfolio:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Toggle Buttons */}
      <div className="flex items-center justify-between bg-gray-900 rounded-xl p-4 border border-gray-700">
        <div className="flex space-x-4">
          <button
            onClick={() => setViewMode("historical")}
            className={`px-6 py-2 rounded-lg font-semibold transition-all ${
              viewMode === "historical"
                ? "bg-blue-600 text-white"
                : "bg-gray-800 text-gray-400 hover:text-gray-300"
            }`}
          >
            📊 Historical Performance
          </button>
          <button
            onClick={() => setViewMode("live")}
            className={`px-6 py-2 rounded-lg font-semibold transition-all ${
              viewMode === "live"
                ? "bg-green-600 text-white"
                : "bg-gray-800 text-gray-400 hover:text-gray-300"
            }`}
          >
            📡 Live Holdings (Q3 2024)
          </button>
        </div>

        <div className="text-sm text-gray-400">
          {viewMode === "historical" ? (
            <span>💎 Shows returns since purchase</span>
          ) : (
            <span>🔄 Updated quarterly from SEC 13F filings</span>
          )}
        </div>
      </div>

      {/* Historical View */}
      {viewMode === "historical" && (
        <div className="space-y-4">
          {/* Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-gray-900 rounded-xl p-6 border border-gray-700">
              <div className="text-gray-400 text-sm mb-1">Weighted Avg Return</div>
              <div className="text-3xl font-bold text-green-400">
                +{historicalData.weighted_avg_return.toFixed(1)}%
              </div>
            </div>
            <div className="bg-gray-900 rounded-xl p-6 border border-gray-700">
              <div className="text-gray-400 text-sm mb-1">Avg Holding Period</div>
              <div className="text-3xl font-bold text-blue-400">
                {historicalData.avg_holding_years.toFixed(1)} yrs
              </div>
            </div>
            <div className="bg-gray-900 rounded-xl p-6 border border-gray-700">
              <div className="text-gray-400 text-sm mb-1">Win Rate</div>
              <div className="text-3xl font-bold text-purple-400">
                {historicalData.winners}/{historicalData.winners + historicalData.losers}
              </div>
            </div>
            {historicalData.best_performer && (
              <div className="bg-gradient-to-br from-yellow-900 to-yellow-800 rounded-xl p-6 border border-yellow-700">
                <div className="text-yellow-200 text-sm mb-1">🏆 Best Performer</div>
                <div className="text-2xl font-bold text-yellow-100">
                  {historicalData.best_performer.symbol}
                </div>
                <div className="text-sm text-yellow-300">
                  +{historicalData.best_performer.return.toFixed(0)}% ({historicalData.best_performer.multiple.toFixed(1)}x)
                </div>
              </div>
            )}
          </div>

          {/* Holdings Table */}
          <div className="bg-gray-900 rounded-xl border border-gray-700 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-700 text-left bg-gray-800">
                    <th className="py-3 px-4">Symbol</th>
                    <th className="py-3 px-4">Company</th>
                    <th className="py-3 px-4 text-right">Buy Date</th>
                    <th className="py-3 px-4 text-right">Buy Price</th>
                    <th className="py-3 px-4 text-right">Current</th>
                    <th className="py-3 px-4 text-right">Return</th>
                    <th className="py-3 px-4 text-right">Multiple</th>
                    <th className="py-3 px-4 text-right">Years</th>
                  </tr>
                </thead>
                <tbody>
                  {historicalData.stocks.map((stock) => (
                    <tr
                      key={stock.symbol}
                      className="border-b border-gray-800 hover:bg-gray-800 transition"
                    >
                      <td className="py-3 px-4">
                        <span className="font-mono font-semibold text-blue-400">
                          {stock.symbol}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-300">{stock.name}</td>
                      <td className="py-3 px-4 text-right text-gray-400 text-sm">
                        {stock.buy_date}
                      </td>
                      <td className="py-3 px-4 text-right text-gray-400">
                        ${stock.buy_price.toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-right font-semibold">
                        ${stock.current_price.toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <span className={stock.return_pct > 0 ? "text-green-400" : "text-red-400"}>
                          {stock.return_pct > 0 ? "+" : ""}
                          {stock.return_pct.toFixed(1)}%
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right font-semibold text-green-400">
                        {stock.multiple ? `${stock.multiple.toFixed(1)}x` : "-"}
                      </td>
                      <td className="py-3 px-4 text-right text-gray-400 text-sm">
                        {stock.holding_period_years.toFixed(1)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Live View */}
      {viewMode === "live" && (
        <div className="space-y-4">
          {loading && (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
              <p className="mt-4 text-gray-400">Loading live portfolio...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-900/20 border border-red-700 rounded-xl p-6 text-red-400">
              {error}
            </div>
          )}

          {liveData && (
            <>
              {/* Live Metrics */}
              <div className="bg-gradient-to-r from-green-900 to-green-800 rounded-xl p-6 border border-green-700">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-semibold text-green-100 mb-2">
                      📡 {liveData.investor}
                    </h3>
                    <p className="text-green-200 text-sm">
                      Report Date: {liveData.report_date} | Source: {liveData.data_source}
                    </p>
                    {liveData.note && (
                      <p className="text-green-300 text-sm mt-2">ℹ️ {liveData.note}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-green-200 text-sm mb-1">Total Portfolio Value</div>
                    <div className="text-3xl font-bold text-green-100">
                      ${liveData.total_value_millions.toFixed(1)}B
                    </div>
                    <div className="text-green-300 text-sm">{liveData.total_holdings} Holdings</div>
                  </div>
                </div>
              </div>

              {/* Live Holdings Table */}
              <div className="bg-gray-900 rounded-xl border border-gray-700 overflow-hidden">
                <div className="p-4 bg-gray-800 border-b border-gray-700 flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Current Holdings (as of {liveData.report_date})</h3>
                  <span className="text-sm text-gray-400">Sorted by portfolio weight</span>
                </div>
                
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-700 text-left bg-gray-800">
                        <th className="py-3 px-4">Rank</th>
                        <th className="py-3 px-4">Symbol</th>
                        <th className="py-3 px-4">Company</th>
                        <th className="py-3 px-4 text-right">Shares</th>
                        <th className="py-3 px-4 text-right">Market Value</th>
                        <th className="py-3 px-4 text-right">Weight</th>
                      </tr>
                    </thead>
                    <tbody>
                      {liveData.holdings.map((holding, index) => (
                        <tr
                          key={holding.ticker}
                          className="border-b border-gray-800 hover:bg-gray-800 transition"
                        >
                          <td className="py-3 px-4">
                            <span className="text-gray-400 font-semibold">#{index + 1}</span>
                          </td>
                          <td className="py-3 px-4">
                            <span className="font-mono font-semibold text-green-400">
                              {holding.ticker}
                            </span>
                          </td>
                          <td className="py-3 px-4 text-gray-300">{holding.name}</td>
                          <td className="py-3 px-4 text-right text-gray-400">
                            {holding.shares.toLocaleString()}
                          </td>
                          <td className="py-3 px-4 text-right font-semibold">
                            ${holding.value_millions.toFixed(1)}M
                          </td>
                          <td className="py-3 px-4 text-right">
                            <div className="flex items-center justify-end space-x-2">
                              <div className="w-24 bg-gray-700 rounded-full h-2">
                                <div
                                  className="bg-green-500 h-2 rounded-full"
                                  style={{ width: `${Math.min(holding.weight_pct, 100)}%` }}
                                />
                              </div>
                              <span className="text-green-400 font-semibold">
                                {holding.weight_pct.toFixed(1)}%
                              </span>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Highlight new positions (if comparing with historical) */}
              <div className="bg-blue-900/20 border border-blue-700 rounded-xl p-4">
                <h4 className="text-blue-400 font-semibold mb-2">💡 Comparing Views:</h4>
                <ul className="text-sm text-blue-300 space-y-1">
                  <li>• <strong>Historical View</strong>: Shows long-term performance from original buy dates</li>
                  <li>• <strong>Live View</strong>: Shows actual current holdings from latest SEC 13F filing</li>
                  <li>• <strong>Updates</strong>: Live data refreshes quarterly (45 days after quarter end)</li>
                  <li>• <strong>New Positions</strong>: May include recently added stocks not in historical view</li>
                </ul>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

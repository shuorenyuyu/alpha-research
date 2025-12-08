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

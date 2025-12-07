"use client";

import { useState, useEffect } from "react";

interface Paper {
  id: number;
  title: string;
  authors: string;
  year: number;
  venue: string;
  citation_count: number;
  summary_zh: string;
  investment_insights: string;
  url: string;
  fetched_at: string;
}

export default function ResearchPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);

  useEffect(() => {
    // Mock data - replace with API call later
    const mockPaper: Paper = {
      id: 1,
      title: "Revised Surgical CAse REport (SCARE) guideline: An update for the age of Artificial Intelligence",
      authors: "Ahmed Kerwan, A. Al-Jabir, et al.",
      year: 2025,
      venue: "Premier Journal of Science",
      citation_count: 669,
      summary_zh: "SCARE 2025指南更新引入AI相关报告标准，提高手术案例报告的透明度和可重复性...",
      investment_insights: "医疗科技公司将受益于这种标准化的指南...",
      url: "https://www.semanticscholar.org/paper/example",
      fetched_at: "2025-12-07",
    };
    
    setTimeout(() => {
      setPapers([mockPaper]);
      setLoading(false);
    }, 500);
  }, []);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading research papers...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black to-gray-900 pt-4">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-white mb-8">AI Research Papers</h1>
      
      <div className="grid gap-6">
        {papers.map((paper) => (
          <div
            key={paper.id}
            className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-lg p-6 hover:border-blue-500 transition-all cursor-pointer group"
            onClick={() => setSelectedPaper(paper)}
          >
            <div className="flex justify-between items-start mb-3">
              <h2 className="text-xl font-semibold text-white flex-1 group-hover:text-blue-400 transition-colors">
                {paper.title}
              </h2>
              <span className="ml-4 px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-sm font-medium">
                {paper.citation_count} citations
              </span>
            </div>
            
            <div className="text-sm text-gray-400 mb-4">
              <span className="font-medium">{paper.authors}</span>
              <span className="mx-2">•</span>
              <span>{paper.venue} ({paper.year})</span>
            </div>

            <div className="prose max-w-none">
              <p className="text-gray-300 line-clamp-3">{paper.summary_zh}</p>
            </div>

            <div className="mt-4 flex gap-2">
              <span className="px-3 py-1 bg-green-500/20 text-green-300 rounded text-sm">
                ✓ Summarized
              </span>
              <span className="px-3 py-1 bg-purple-500/20 text-purple-300 rounded text-sm">
                Investment Analysis
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Modal for full paper view */}
      {selectedPaper && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedPaper(null)}
        >
          <div 
            className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto p-8"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-start mb-6">
              <h2 className="text-2xl font-bold text-gray-900 flex-1 pr-4">
                {selectedPaper.title}
              </h2>
              <button
                onClick={() => setSelectedPaper(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="mb-6">
              <p className="text-gray-600"><strong>Authors:</strong> {selectedPaper.authors}</p>
              <p className="text-gray-600"><strong>Venue:</strong> {selectedPaper.venue} ({selectedPaper.year})</p>
              <p className="text-gray-600"><strong>Citations:</strong> {selectedPaper.citation_count}</p>
              <a href={selectedPaper.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                View Paper →
              </a>
            </div>

            <div className="border-t pt-6">
              <h3 className="text-xl font-semibold mb-3">中文摘要</h3>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {selectedPaper.summary_zh}
                </p>
              </div>
            </div>

            <div className="border-t mt-6 pt-6">
              <h3 className="text-xl font-semibold mb-3">投资洞察</h3>
              <div className="prose max-w-none">
                <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">
                  {selectedPaper.investment_insights}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
}

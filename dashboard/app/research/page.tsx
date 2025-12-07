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
    const fetchPapers = async () => {
      try {
        const response = await fetch('http://localhost:8001/api/research/papers?limit=50');
        if (response.ok) {
          const data = await response.json();
          setPapers(data);
        } else {
          console.error('Failed to fetch papers');
        }
      } catch (error) {
        console.error('Error fetching papers:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPapers();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-black to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading research papers...</p>
        </div>
      </div>
    );
  }

  if (!loading && papers.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-black to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-2xl text-gray-400">No research papers found</p>
          <p className="text-gray-500 mt-2">Start the backend API to load papers from research-tracker</p>
        </div>
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
          className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 z-50"
          onClick={() => setSelectedPaper(null)}
        >
          <div 
            className="bg-gray-900 border border-gray-700 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto p-8"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex justify-between items-start mb-6">
              <h2 className="text-2xl font-bold text-white flex-1 pr-4">
                {selectedPaper.title}
              </h2>
              <button
                onClick={() => setSelectedPaper(null)}
                className="text-gray-400 hover:text-white text-3xl font-light leading-none"
              >
                ×
              </button>
            </div>

            <div className="mb-6 space-y-2">
              <p className="text-gray-300"><strong className="text-white">Authors:</strong> {selectedPaper.authors}</p>
              <p className="text-gray-300"><strong className="text-white">Venue:</strong> {selectedPaper.venue} ({selectedPaper.year})</p>
              <p className="text-gray-300"><strong className="text-white">Citations:</strong> {selectedPaper.citation_count}</p>
              <a href={selectedPaper.url} target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 hover:underline inline-block">
                View Paper →
              </a>
            </div>

            <div className="border-t border-gray-700 pt-6">
              <h3 className="text-xl font-semibold mb-4 text-white">📄 中文摘要</h3>
              <div className="prose prose-invert prose-sm max-w-none">
                <div 
                  className="whitespace-pre-wrap leading-relaxed text-gray-300"
                  dangerouslySetInnerHTML={{
                    __html: selectedPaper.summary_zh
                      ? selectedPaper.summary_zh
                          .replace(/##\s+(.+)/g, '<h3 class="text-lg font-bold mt-4 mb-2 text-white">$1</h3>')
                          .replace(/\*\*(.+?)\*\*/g, '<strong class="text-white">$1</strong>')
                          .replace(/\n\n/g, '<br/><br/>')
                      : '暂无摘要'
                  }}
                />
              </div>
            </div>

            <div className="border-t border-gray-700 mt-6 pt-6">
              <h3 className="text-xl font-semibold mb-4 text-white">💡 投资洞察</h3>
              <div className="prose prose-invert prose-sm max-w-none">
                <div 
                  className="whitespace-pre-wrap leading-relaxed text-gray-300"
                  dangerouslySetInnerHTML={{
                    __html: selectedPaper.investment_insights
                      ? selectedPaper.investment_insights
                          .replace(/###\s+(.+)/g, '<h4 class="text-base font-bold mt-3 mb-2 text-white">$1</h4>')
                          .replace(/##\s+(.+)/g, '<h3 class="text-lg font-bold mt-4 mb-2 text-white">$1</h3>')
                          .replace(/\*\*(.+?)\*\*/g, '<strong class="text-white">$1</strong>')
                          .replace(/\n\n/g, '<br/><br/>')
                      : '暂无投资洞察'
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
}

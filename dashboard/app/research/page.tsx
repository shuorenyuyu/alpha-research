"use client";

import { useState, useEffect } from "react";

interface WechatArticle {
  filename: string;
  date: string;
  title: string;
}

interface SearchPaper {
  title: string;
  authors: string[];
  published_date?: string;
  citations?: number;
  url?: string;
  abstract?: string;
}

export default function ResearchPage() {
  const [articles, setArticles] = useState<WechatArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedArticle, setSelectedArticle] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  
  // Custom theme search state
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [searchTheme, setSearchTheme] = useState('');
  const [searchResults, setSearchResults] = useState<SearchPaper[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchSource, setSearchSource] = useState<'all' | 'arxiv' | 'semantic_scholar'>('all');

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        console.log('Fetching articles from /api/research/wechat/list');
        const response = await fetch('/api/research/wechat/list', {
          cache: 'no-store',
          headers: {
            'Cache-Control': 'no-cache'
          }
        });
        console.log('Response status:', response.status);
        if (response.ok) {
          const data = await response.json();
          console.log('Articles data:', data);
          // Backend now returns objects with filename, date, and title
          setArticles(data.articles);
        } else {
          const errorText = `Failed to fetch articles: ${response.status}`;
          console.error(errorText);
          setError(errorText);
        }
      } catch (error) {
        const errorMsg = 'Error fetching articles: ' + String(error);
        console.error(errorMsg);
        setError(errorMsg);
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  const generatePaper = async () => {
    if (!confirm('Generate a new AI research paper? This will fetch from ArXiv and create AI summaries (may take 2-5 minutes).')) {
      return;
    }

    setGenerating(true);
    try {
      const response = await fetch('/api/research/wechat/generate', {
        method: 'POST',
      });

      const data = await response.json();

      if (response.ok) {
        const message = data.message || 'Research paper generated successfully!';
        const traceId = data.trace_id ? ` (Trace ID: ${data.trace_id})` : '';
        alert(message + traceId + '\n\nRefreshing list...');
        window.location.reload();
      } else {
        // Display detailed error information
        let errorMsg = data.error || 'Unknown error';
        
        // Add trace ID if available for debugging
        if (data.detail?.trace_id) {
          errorMsg += `\n\nTrace ID: ${data.detail.trace_id}`;
          errorMsg += '\nCheck the backend logs for more details.';
        }
        
        // Add stderr details if available (truncated for readability)
        if (data.detail?.stderr) {
          const stderrPreview = data.detail.stderr.split('\n').slice(0, 5).join('\n');
          errorMsg += `\n\nError details:\n${stderrPreview}`;
          if (data.detail.stderr.split('\n').length > 5) {
            errorMsg += '\n... (see backend logs for full error)';
          }
        }
        
        // Add suggestion if available
        if (data.detail?.suggestion) {
          errorMsg += `\n\nSuggestion: ${data.detail.suggestion}`;
        }
        
        alert(`Failed to generate paper:\n\n${errorMsg}`);
      }
    } catch (error) {
      console.error('Error generating paper:', error);
      alert('Error generating paper: Failed to connect to the server.\n\nPlease ensure the backend API is running on port 8000.');
    } finally {
      setGenerating(false);
    }
  };

  const deleteArticle = async (filename: string, title: string) => {
    if (!confirm(`Delete article: ${title}?`)) {
      return;
    }
    
    try {
      const response = await fetch(`/api/research/wechat/${filename}`, {
        method: 'DELETE'
      });
      
      if (response.ok) {
        // Remove from list
        setArticles(articles.filter(a => a.filename !== filename));
        alert('Article deleted successfully');
      } else {
        alert('Failed to delete article');
      }
    } catch (error) {
      console.error('Error deleting article:', error);
      alert('Error deleting article');
    }
  };
  
  const searchPapersByTheme = async () => {
    if (!searchTheme.trim()) {
      alert('Please enter a research theme');
      return;
    }
    
    setSearching(true);
    setSearchResults([]);
    
    try {
      const response = await fetch('/api/research/search/theme', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          theme: searchTheme,
          max_results: 10,
          source: searchSource
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setSearchResults(data.papers || []);
        if (data.papers?.length === 0) {
          alert(`No papers found for "${searchTheme}". Try a different theme or source.`);
        }
      } else {
        const errorMsg = data.detail?.error || 'Search failed';
        const traceId = data.detail?.trace_id ? ` (Trace ID: ${data.detail.trace_id})` : '';
        alert(`Search failed: ${errorMsg}${traceId}`);
      }
    } catch (error) {
      console.error('Error searching papers:', error);
      alert('Error searching papers: Failed to connect to the server.\n\nPlease ensure the backend API is running on port 8000.');
    } finally {
      setSearching(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-black to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading research articles...</p>
        </div>
      </div>
    );
  }

  if (!loading && (articles.length === 0 || error)) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-black to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-2xl text-gray-400">
            {error ? 'Error loading articles' : 'No research articles found'}
          </p>
          <p className="text-gray-500 mt-2">
            {error || 'Articles will be generated daily by research-tracker'}
          </p>
          {error && (
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Retry
            </button>
          )}
        </div>
      </div>
    );
  }

  // If an article is selected, show it in full screen
  if (selectedArticle) {
    return (
      <div className="min-h-screen bg-black">
        <div className="sticky top-0 z-50 bg-gray-900 border-b border-gray-700 px-4 py-3">
          <button
            onClick={() => setSelectedArticle(null)}
            className="text-blue-400 hover:text-blue-300 flex items-center gap-2"
          >
            ← Back to Articles
          </button>
        </div>
        <iframe
          src={`/api/research/wechat/${selectedArticle}`}
          className="w-full"
          style={{ height: 'calc(100vh - 57px)' }}
          title="Research Article"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black to-gray-900 pt-4">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white">🔬 AI Research Papers</h1>
            <p className="text-gray-400 mt-2">
              Daily AI research paper analysis with Chinese summaries and investment insights
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowSearchModal(true)}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:from-purple-500 hover:to-pink-500 transition-all transform hover:scale-105"
            >
              🔍 Custom Theme Search
            </button>
            <button
              onClick={generatePaper}
              disabled={generating}
              className="px-6 py-3 bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg font-semibold hover:from-green-500 hover:to-blue-500 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
            >
              {generating ? '🔄 Generating...' : '🤖 Auto-Generate Paper'}
            </button>
          </div>
        </div>
        
        {/* Custom Theme Search Modal */}
        {showSearchModal && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="bg-gray-800 border border-gray-700 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-700">
                <div className="flex justify-between items-center">
                  <h2 className="text-2xl font-bold text-white">🔍 Search Papers by Theme</h2>
                  <button
                    onClick={() => {
                      setShowSearchModal(false);
                      setSearchResults([]);
                      setSearchTheme('');
                    }}
                    className="text-gray-400 hover:text-white text-2xl"
                  >
                    ×
                  </button>
                </div>
                <p className="text-gray-400 mt-2">
                  Search for research papers on specific topics using arXiv and Semantic Scholar
                </p>
              </div>
              
              <div className="p-6">
                {/* Search Form */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Research Theme
                    </label>
                    <input
                      type="text"
                      value={searchTheme}
                      onChange={(e) => setSearchTheme(e.target.value)}
                      placeholder="e.g., transformers, reinforcement learning, computer vision..."
                      className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                      onKeyPress={(e) => e.key === 'Enter' && searchPapersByTheme()}
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Data Source
                    </label>
                    <div className="flex gap-2">
                      {(['all', 'arxiv', 'semantic_scholar'] as const).map((source) => (
                        <button
                          key={source}
                          onClick={() => setSearchSource(source)}
                          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                            searchSource === source
                              ? 'bg-purple-600 text-white'
                              : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                          }`}
                        >
                          {source === 'all' ? '🌐 All' : source === 'arxiv' ? '📄 arXiv' : '🔬 Semantic Scholar'}
                        </button>
                      ))}
                    </div>
                  </div>
                  
                  <button
                    onClick={searchPapersByTheme}
                    disabled={searching || !searchTheme.trim()}
                    className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold hover:from-purple-500 hover:to-pink-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {searching ? '🔄 Searching...' : '🔍 Search Papers'}
                  </button>
                </div>
                
                {/* Search Results */}
                {searchResults.length > 0 && (
                  <div className="mt-6 space-y-4">
                    <h3 className="text-xl font-semibold text-white">
                      📚 Found {searchResults.length} papers
                    </h3>
                    {searchResults.map((paper, index) => (
                      <div
                        key={index}
                        className="bg-gray-700/50 border border-gray-600 rounded-lg p-4 hover:border-purple-500 transition-all"
                      >
                        <h4 className="text-lg font-semibold text-white mb-2">
                          {paper.title}
                        </h4>
                        {paper.authors && paper.authors.length > 0 && (
                          <p className="text-sm text-gray-400 mb-2">
                            👥 {paper.authors.slice(0, 3).join(', ')}
                            {paper.authors.length > 3 && ' et al.'}
                          </p>
                        )}
                        <div className="flex gap-3 text-sm text-gray-300">
                          {paper.published_date && (
                            <span>📅 {paper.published_date}</span>
                          )}
                          {paper.citations !== undefined && paper.citations !== null && (
                            <span>📊 {paper.citations.toLocaleString()} citations</span>
                          )}
                        </div>
                        {paper.abstract && (
                          <p className="text-sm text-gray-400 mt-2 line-clamp-3">
                            {paper.abstract}
                          </p>
                        )}
                        {paper.url && (
                          <a
                            href={paper.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-block mt-2 text-purple-400 hover:text-purple-300 text-sm"
                          >
                            🔗 View Paper →
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      
        <div className="grid gap-6">
          {articles.map((article) => (
            <div
              key={article.filename}
              className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-lg p-6 hover:border-blue-500 transition-all group"
            >
              <div className="flex justify-between items-start">
                <div 
                  className="flex-1 cursor-pointer"
                  onClick={() => setSelectedArticle(article.filename)}
                >
                  <h2 className="text-2xl font-semibold text-white group-hover:text-blue-400 transition-colors">
                    {article.title}
                  </h2>
                  <p className="text-gray-400 mt-2">
                    📅 {article.date.slice(0, 4)}-{article.date.slice(4, 6)}-{article.date.slice(6, 8)}
                  </p>
                </div>
                <div className="flex gap-2 items-start">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteArticle(article.filename, article.title);
                    }}
                    className="px-3 py-1 bg-red-500/20 hover:bg-red-500/40 text-red-300 hover:text-red-200 rounded text-sm transition-colors"
                    title="Delete article"
                  >
                    🗑️ Delete
                  </button>
                  <span 
                    className="text-blue-400 text-xl cursor-pointer"
                    onClick={() => setSelectedArticle(article.filename)}
                  >
                    →
                  </span>
                </div>
              </div>
              
              <div className="mt-4 flex gap-2"
                onClick={() => setSelectedArticle(article.filename)}
              >
                <span className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded text-sm">
                  📄 Research Analysis
                </span>
                <span className="px-3 py-1 bg-green-500/20 text-green-300 rounded text-sm">
                  💰 Investment Insights
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

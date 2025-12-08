"use client";

import { useState, useEffect } from "react";

interface WechatArticle {
  filename: string;
  date: string;
  title: string;
}

export default function ResearchPage() {
  const [articles, setArticles] = useState<WechatArticle[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedArticle, setSelectedArticle] = useState<string | null>(null);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const apiHost = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
        const response = await fetch(`http://${apiHost}:8001/api/research/wechat/list`);
        if (response.ok) {
          const data = await response.json();
          // Parse article filenames to extract dates and create article objects
          const articleList = data.articles.map((filename: string) => {
            const dateMatch = filename.match(/wechat_(\d{8})\.html/);
            const date = dateMatch ? dateMatch[1] : 'unknown';
            return {
              filename,
              date,
              title: `AI Research - ${date.slice(0, 4)}-${date.slice(4, 6)}-${date.slice(6, 8)}`
            };
          });
          setArticles(articleList);
        } else {
          console.error('Failed to fetch articles');
        }
      } catch (error) {
        console.error('Error fetching articles:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

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

  if (!loading && articles.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-black to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-2xl text-gray-400">No research articles found</p>
          <p className="text-gray-500 mt-2">Articles will be generated daily by research-tracker</p>
        </div>
      </div>
    );
  }

  // If an article is selected, show it in full screen
  if (selectedArticle) {
    const apiHost = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
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
          src={`http://${apiHost}:8001/api/research/wechat/${selectedArticle}`}
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
        <h1 className="text-4xl font-bold text-white mb-8">🔬 AI Research Papers</h1>
        <p className="text-gray-400 mb-8">
          Daily AI research paper analysis with Chinese summaries and investment insights
        </p>
      
        <div className="grid gap-6">
          {articles.map((article) => (
            <div
              key={article.filename}
              className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-lg p-6 hover:border-blue-500 transition-all cursor-pointer group"
              onClick={() => setSelectedArticle(article.filename)}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-2xl font-semibold text-white group-hover:text-blue-400 transition-colors">
                    {article.title}
                  </h2>
                  <p className="text-gray-400 mt-2">
                    Published: {article.date.slice(0, 4)}-{article.date.slice(4, 6)}-{article.date.slice(6, 8)}
                  </p>
                </div>
                <span className="text-blue-400 text-xl">→</span>
              </div>
              
              <div className="mt-4 flex gap-2">
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

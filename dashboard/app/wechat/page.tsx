"use client";

import { useState, useEffect } from "react";

export default function WechatPage() {
  const [articles, setArticles] = useState<string[]>([]);
  const [selectedArticle, setSelectedArticle] = useState<string | null>(null);
  const [articleContent, setArticleContent] = useState<string>("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchArticles = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/research/wechat/list');
        if (response.ok) {
          const data = await response.json();
          setArticles(data.articles || []);
        }
      } catch (error) {
        console.error('Error fetching articles:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchArticles();
  }, []);

  const loadArticle = async (filename: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/research/wechat/${filename}`);
      if (response.ok) {
        const html = await response.text();
        setArticleContent(html);
        setSelectedArticle(filename);
      }
    } catch (error) {
      console.error('Error loading article:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-black to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading WeChat articles...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-black to-gray-900 pt-4">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-white mb-8">📱 WeChat Research Articles</h1>

        {articles.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-2xl text-gray-400">No WeChat articles found</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {articles.map((article) => (
              <div
                key={article}
                onClick={() => loadArticle(article)}
                className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-lg p-6 hover:border-green-500 transition-all cursor-pointer group"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">📄</span>
                    <h2 className="text-lg font-semibold text-white group-hover:text-green-400 transition-colors">
                      {article.replace('.html', '').replace('wechat_', 'WeChat Article - ')}
                    </h2>
                  </div>
                  <span className="text-gray-400 text-sm">Click to view →</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Modal for article view */}
        {selectedArticle && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50"
            onClick={() => {
              setSelectedArticle(null);
              setArticleContent("");
            }}
          >
            <div 
              className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center z-10">
                <h2 className="text-xl font-bold text-gray-900">
                  {selectedArticle.replace('.html', '').replace('wechat_', 'WeChat Article - ')}
                </h2>
                <button
                  onClick={() => {
                    setSelectedArticle(null);
                    setArticleContent("");
                  }}
                  className="text-gray-500 hover:text-gray-700 text-3xl leading-none"
                >
                  ×
                </button>
              </div>
              <div 
                className="p-6"
                dangerouslySetInnerHTML={{ __html: articleContent }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

import React, { useState, useRef, useEffect } from 'react';
import useUserLimits from '../hooks/useUserLimits';
import { getChatResponse } from '../apiClient';

// DealCard Component
const DealCard = ({ deal }) => {
  const [expanded, setExpanded] = React.useState(false);
  
  return (
    <div className="overflow-hidden bg-white rounded-2xl shadow-xl border border-gray-100 transform transition-all hover:scale-[1.01]">
      <div className="p-5 border-b border-gray-100">
        <h3 className="text-lg font-bold text-gray-900">{deal.product_name}</h3>
        <p className="text-sm font-medium text-gray-500">Store: {deal.store}</p>
        {deal.sku && <p className="text-xs text-gray-400 mt-1">SKU: {deal.sku}</p>}
      </div>
      <div className="p-5 bg-gray-50/70">
        <div className="flex items-baseline">
          <span className="text-4xl font-extrabold text-red-600">${deal.price.toFixed(2)}</span>
          {deal.original_price && deal.original_price > 0 && (
            <span className="ml-3 text-xl text-gray-400 line-through">${deal.original_price.toFixed(2)}</span>
          )}
        </div>
        {deal.bundle_deal && deal.free_item && (
          <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm font-semibold text-green-800">🎁 Bundle Deal!</p>
            <p className="text-xs text-green-700 mt-1">Buy this + Get: {deal.free_item}</p>
          </div>
        )}
      </div>
      
      {expanded && (
        <div className="p-5 border-t border-gray-100 bg-gray-50">
          {deal.bundle_deal && deal.required_purchase && (
            <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded">
              <h4 className="text-sm font-semibold text-blue-800 mb-1">📦 How to Get This Deal:</h4>
              <p className="text-sm text-blue-700">Purchase: {deal.required_purchase}</p>
              {deal.free_item && (
                <p className="text-sm text-blue-700 mt-1">Get Free: {deal.free_item}</p>
              )}
            </div>
          )}
          {deal.deal_conditions && deal.deal_conditions.length > 0 && (
            <div className="mb-3">
              <h4 className="text-sm font-semibold text-gray-700 mb-1">Conditions:</h4>
              <ul className="text-sm text-gray-600 list-disc list-inside">
                {deal.deal_conditions.map((condition, idx) => (
                  <li key={idx}>{condition}</li>
                ))}
              </ul>
            </div>
          )}
          {deal.attributes && deal.attributes.length > 0 && (
            <div className="mb-3">
              <h4 className="text-sm font-semibold text-gray-700 mb-1">Features:</h4>
              <div className="flex flex-wrap gap-2">
                {deal.attributes.map((attr, idx) => (
                  <span key={idx} className="px-2 py-1 bg-indigo-100 text-indigo-700 rounded text-xs">
                    {attr}
                  </span>
                ))}
              </div>
            </div>
          )}
          {deal.valid_from && deal.valid_to && (
            <div className="text-xs text-gray-500 mt-2">
              Valid: {new Date(deal.valid_from).toLocaleDateString()} - {new Date(deal.valid_to).toLocaleDateString()}
            </div>
          )}
        </div>
      )}
      
      <div className="flex items-center justify-between p-5">
        <span className={`inline-block px-3 py-1 text-xs font-semibold uppercase rounded-full ${deal.in_store_only ? 'bg-yellow-100 text-yellow-800' : 'bg-indigo-100 text-indigo-800'}`}>
          {deal.in_store_only ? 'In-Store Only' : deal.deal_type}
        </span>
        <button 
          onClick={() => setExpanded(!expanded)} 
          className="text-sm font-semibold text-indigo-600 hover:text-indigo-500"
        >
          {expanded ? 'Hide Details' : 'View Deal'} {expanded ? '↑' : '→'}
        </button>
      </div>
    </div>
  );
};

// ChatBubble Component
const ChatBubble = ({ message }) => {
  const { sender, text, sources } = message;
  const isUser = sender === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="px-5 py-3 text-white bg-indigo-600 rounded-t-2xl rounded-l-2xl shadow-lg" style={{ maxWidth: '80%' }}>
          <p>{text}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col space-y-4">
      <div className="flex justify-start">
        <div className="px-5 py-3 bg-white border border-gray-100 rounded-t-2xl rounded-r-2xl shadow-lg" style={{ maxWidth: '80%' }}>
          <p className="text-gray-800" dangerouslySetInnerHTML={{ __html: text.replace(/\n/g, '<br />') }} />
        </div>
      </div>
      {sources && sources.length > 0 && (
        <div className="space-y-5">
          {sources.map((deal, index) => (
            <DealCard key={index} deal={deal} />
          ))}
        </div>
      )}
    </div>
  );
};

// Main Chat Interface
const ChatInterface = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    { sender: 'ai', text: "Hi! I'm DealZen, your Black Friday assistant. Ask me about any deal!" }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const { hasReachedLimit, remainingQuestions, incrementCount } = useUserLimits(10);
  const chatLogRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (chatLogRef.current) {
      chatLogRef.current.scrollTop = chatLogRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || hasReachedLimit || isLoading) return;

    const userMessage = { sender: 'user', text: query };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setQuery('');

    try {
      const response = await getChatResponse(query);
      const aiMessage = { sender: 'ai', text: response.answer, sources: response.source_deals };
      setMessages(prev => [...prev, aiMessage]);
      incrementCount();
    } catch (error) {
      console.error("Failed to get chat response:", error);
      const errorMessage = { sender: 'ai', text: 'Sorry, I ran into an error. Please try again.' };
      setMessages(prev => [...prev, errorMessage]);
    }

    setIsLoading(false);
  };

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto bg-gray-50">
      <header className="sticky top-0 z-10 flex items-center justify-between p-4 shadow-md bg-gradient-to-r from-indigo-600 to-indigo-500">
        <h1 className="text-xl font-bold text-white">DealZen</h1>
        <span className="px-3 py-1 text-sm font-semibold text-indigo-700 bg-white rounded-full shadow-sm">
          {remainingQuestions}/10
        </span>
      </header>

      <main ref={chatLogRef} className="flex-1 p-4 overflow-y-auto chat-log space-y-8">
        {messages.map((msg, index) => (
          <ChatBubble key={index} message={msg} />
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="px-5 py-3 bg-white border border-gray-100 rounded-t-2xl rounded-r-2xl shadow-lg">
              <p className="text-gray-500 italic">Finding deals...</p>
            </div>
          </div>
        )}
      </main>

      <form onSubmit={handleSubmit} className="sticky bottom-0 z-10 p-4 bg-white shadow-[0_-4px_12px_rgba(0,0,0,0.03)]">
        <div className="flex items-center space-x-3">
          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={hasReachedLimit ? 'You have reached your 10 question limit' : 'Ask about a deal... (250)'}
            maxLength="250"
            disabled={hasReachedLimit || isLoading}
            className="flex-1 px-5 py-3 text-gray-800 bg-gray-100 border-transparent rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
          />
          <button 
            type="submit" 
            disabled={hasReachedLimit || isLoading}
            className="p-3 text-white bg-indigo-600 rounded-xl shadow-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:bg-gray-400"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-6 h-6">
              <path d="M3.105 3.105a.5.5 0 01.707 0L19.5 18.293V12.5a.5.5 0 011 0v8a.5.5 0 01-.5.5h-8a.5.5 0 010-1h5.793L3.105 3.812a.5.5 0 010-.707z" />
            </svg>
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;


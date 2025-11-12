import React, { useState, useRef, useEffect } from 'react';
import useUserLimits from '../hooks/useUserLimits';
import { getChatResponse } from '../apiClient';

// Helper function to calculate savings
const calculateSavings = (deal) => {
  if (!deal.original_price || deal.original_price <= deal.price) return null;
  const savingsAmount = deal.original_price - deal.price;
  const savingsPercent = Math.round((savingsAmount / deal.original_price) * 100);
  return { amount: savingsAmount, percent: savingsPercent };
};

// Helper function to get store shopping URL
const getStoreUrl = (deal) => {
  const storeName = deal.store.toUpperCase().trim();
  const sku = deal.sku || '';
  
  // Clean up product name by removing common marketing terms that hurt search accuracy
  let cleanProductName = deal.product_name;
  const marketingTerms = ['EXCLUSIVE', 'NEW', 'SPECIAL BUY', 'ONLINE ONLY', 'LIMITED TIME'];
  marketingTerms.forEach(term => {
    cleanProductName = cleanProductName.replace(new RegExp(`\\b${term}\\b`, 'gi'), '');
  });
  cleanProductName = cleanProductName.trim().replace(/\s+/g, ' '); // Clean extra spaces
  
  // For better search results: use cleaned product name + SKU
  // SKU is most reliable, product name provides context
  const searchTerm = sku 
    ? encodeURIComponent(`${cleanProductName} ${sku}`)
    : encodeURIComponent(cleanProductName);
  
  const searchUrls = {
    'HOMEDEPOT': `https://www.homedepot.com/s/${searchTerm}`,
    'HOME DEPOT': `https://www.homedepot.com/s/${searchTerm}`,
    'WALMART': `https://www.walmart.com/search?q=${searchTerm}`,
    'TARGET': `https://www.target.com/s?searchTerm=${searchTerm}`,
    'BESTBUY': `https://www.bestbuy.com/site/searchpage.jsp?st=${searchTerm}`,
    'BEST BUY': `https://www.bestbuy.com/site/searchpage.jsp?st=${searchTerm}`,
    'LOWES': `https://www.lowes.com/search?searchTerm=${searchTerm}`,
    'KOHLS': `https://www.kohls.com/search.jsp?search=${searchTerm}`,
    "KOHL'S": `https://www.kohls.com/search.jsp?search=${searchTerm}`,
    'MACYS': `https://www.macys.com/shop/featured/${searchTerm}`,
    "MACY'S": `https://www.macys.com/shop/featured/${searchTerm}`,
  };
  
  return searchUrls[storeName] || `https://www.google.com/search?q=${searchTerm}+${storeName}`;
};

// Helper function to handle Shop Now click
const handleShopNow = (deal) => {
  const url = getStoreUrl(deal);
  
  // Log for analytics (optional)
  console.log('Shop Now clicked:', {
    product: deal.product_name,
    store: deal.store,
    price: deal.price,
    url: url
  });
  
  // Open in new tab
  window.open(url, '_blank', 'noopener,noreferrer');
};

// DealCard Component (Improved UI)
const DealCard = ({ deal }) => {
  const [expanded, setExpanded] = React.useState(false);
  const savings = calculateSavings(deal);
  
  return (
    <div className="relative overflow-hidden bg-white rounded-2xl shadow-xl border border-gray-100 transform transition-all hover:shadow-2xl hover:-translate-y-1">
      
      {/* Savings Badge (Top-Right) */}
      {savings && (
        <div className="absolute top-4 right-4 z-10 bg-gradient-to-r from-red-600 to-red-500 text-white px-4 py-2 rounded-full shadow-lg">
          <div className="text-center">
            <div className="text-lg font-black leading-tight">${savings.amount.toFixed(0)} OFF</div>
            <div className="text-xs font-semibold opacity-90">{savings.percent}% SAVINGS</div>
          </div>
        </div>
      )}
      
      {/* Hero Section with Gradient Background */}
      <div className="bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 p-6 pb-8">
        <div className="pr-24"> {/* Add padding to avoid overlap with savings badge */}
          <h3 className="text-xl font-extrabold text-gray-900 mb-3 leading-tight">
            {deal.product_name}
          </h3>
          
          {/* Store Badge and Type */}
          <div className="flex flex-wrap items-center gap-2 mb-4">
            <span className="inline-flex items-center px-3 py-1 bg-white rounded-full shadow-sm">
              <span className="text-sm font-bold text-indigo-600">🏪 {deal.store}</span>
            </span>
            {deal.in_store_only && (
              <span className="inline-flex items-center px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-semibold">
                📍 In-Store Only
              </span>
            )}
            {!deal.in_store_only && deal.deal_type && (
              <span className="inline-flex items-center px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs font-semibold">
                {deal.deal_type}
              </span>
            )}
          </div>
          
          {/* Price (Large and Prominent) */}
          <div className="flex items-end gap-3">
            <div className="text-5xl font-black text-indigo-600">
              ${Math.floor(deal.price)}
              <span className="text-3xl">.{(deal.price % 1).toFixed(2).slice(2)}</span>
            </div>
            {deal.original_price && deal.original_price > deal.price && (
              <div className="text-2xl text-gray-400 line-through mb-2">
                ${deal.original_price.toFixed(0)}
              </div>
            )}
          </div>
          
          {/* SKU (Small, Subtle) */}
          {deal.sku && (
            <p className="text-xs text-gray-500 mt-2">SKU: {deal.sku}</p>
          )}
        </div>
      </div>
      
      {/* Bundle Deal Highlight */}
      {deal.bundle_deal && deal.free_item && (
        <div className="mx-4 -mt-4 mb-4 p-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-xl shadow-lg">
          <div className="flex items-start gap-3">
            <span className="text-2xl">🎁</span>
            <div>
              <p className="font-bold text-sm">Special Bundle Deal!</p>
              <p className="text-sm opacity-90 mt-1">Buy this + Get: {deal.free_item}</p>
            </div>
          </div>
        </div>
      )}
      
      {/* Expanded Details */}
      {expanded && (
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-100">
          {deal.bundle_deal && deal.required_purchase && (
            <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="text-sm font-bold text-blue-900 mb-2">📦 How to Get This Deal:</h4>
              <p className="text-sm text-blue-800">Purchase: {deal.required_purchase}</p>
              {deal.free_item && (
                <p className="text-sm text-blue-800 mt-1">Get Free: {deal.free_item}</p>
              )}
            </div>
          )}
          
          {deal.deal_conditions && deal.deal_conditions.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-bold text-gray-800 mb-2">📋 Conditions:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                {deal.deal_conditions.map((condition, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-indigo-500 mt-0.5">•</span>
                    <span>{condition}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {deal.attributes && deal.attributes.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-bold text-gray-800 mb-2">✨ Features:</h4>
              <div className="flex flex-wrap gap-2">
                {deal.attributes.map((attr, idx) => (
                  <span key={idx} className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-xs font-medium">
                    {attr}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {deal.valid_from && deal.valid_to && (
            <div className="text-xs text-gray-500 bg-gray-100 px-3 py-2 rounded">
              ⏰ Valid: {new Date(deal.valid_from).toLocaleDateString()} - {new Date(deal.valid_to).toLocaleDateString()}
            </div>
          )}
        </div>
      )}
      
      {/* Action Buttons */}
      <div className="p-4 bg-white space-y-3">
        {/* Primary CTA: Shop Now */}
        <button 
          onClick={() => handleShopNow(deal)}
          className="w-full flex items-center justify-center gap-3 px-6 py-3.5 bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-700 hover:to-indigo-600 text-white rounded-xl font-bold text-base shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          Shop Now at {deal.store}
        </button>
        
        {/* Secondary Action: View Full Details */}
        <button 
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-semibold text-sm transition-colors"
        >
          <span>{expanded ? 'Hide' : 'View'} Full Details</span>
          <svg className={`w-4 h-4 transform transition-transform ${expanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
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
  
  // TODO: Re-enable user limits after testing
  // const { hasReachedLimit, remainingQuestions, incrementCount } = useUserLimits(10);
  const hasReachedLimit = false; // Temporarily disabled for testing
  const remainingQuestions = '∞'; // Unlimited for testing
  const incrementCount = () => {}; // No-op for testing
  
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


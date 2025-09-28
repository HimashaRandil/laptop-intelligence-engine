'use client';

import { useState, useEffect, useRef } from 'react';
import { MessageSquare, X, Send, Bot, User, Minimize2, Maximize2 } from 'lucide-react';

interface ChatMessage {
    id: string;
    content: string;
    role: 'user' | 'assistant';
    timestamp: Date;
}

interface ChatResponse {
    response: string;
    conversation_id: string;
    status: string;
}

const AI_API_URL = process.env.NEXT_PUBLIC_AI_API_URL || 'http://localhost:8001';

export default function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [conversationId, setConversationId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const messagesEndRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Focus input when chat opens
    useEffect(() => {
        if (isOpen && !isMinimized) {
            inputRef.current?.focus();
        }
    }, [isOpen, isMinimized]);

    // Initialize with welcome message
    useEffect(() => {
        if (messages.length === 0) {
            setMessages([{
                id: 'welcome',
                content: "Hi! I'm your laptop shopping assistant. I can help you find the perfect laptop, compare specifications, answer questions about our products, or provide personalized recommendations. What would you like to know?",
                role: 'assistant',
                timestamp: new Date()
            }]);
        }
    }, [messages.length]);

    const sendMessage = async () => {
        if (!inputMessage.trim() || isLoading) return;

        const userMessage: ChatMessage = {
            id: Date.now().toString(),
            content: inputMessage.trim(),
            role: 'user',
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch(`${AI_API_URL}/ai/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage.content,
                    conversation_id: conversationId
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data: ChatResponse = await response.json();

            setConversationId(data.conversation_id);

            const assistantMessage: ChatMessage = {
                id: (Date.now() + 1).toString(),
                content: data.response,
                role: 'assistant',
                timestamp: new Date()
            };

            setMessages(prev => [...prev, assistantMessage]);
        } catch (err) {
            console.error('Chat error:', err);
            setError('Sorry, I encountered an error. Please try again.');

            const errorMessage: ChatMessage = {
                id: (Date.now() + 1).toString(),
                content: 'Sorry, I encountered an error. Please try again.',
                role: 'assistant',
                timestamp: new Date()
            };

            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const toggleChat = () => {
        setIsOpen(!isOpen);
        setIsMinimized(false);
    };

    const toggleMinimize = () => {
        setIsMinimized(!isMinimized);
    };

    const clearChat = () => {
        setMessages([{
            id: 'welcome',
            content: "Hi! I'm your laptop shopping assistant. I can help you find the perfect laptop, compare specifications, answer questions about our products, or provide personalized recommendations. What would you like to know?",
            role: 'assistant',
            timestamp: new Date()
        }]);
        setConversationId(null);
        setError(null);
    };

    const formatTime = (date: Date) => {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <>
            {/* Chat Button */}
            {!isOpen && (
                <button
                    onClick={toggleChat}
                    className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition-all duration-200 flex items-center justify-center z-50 hover:scale-105"
                    aria-label="Open chat"
                >
                    <MessageSquare size={24} />
                </button>
            )}

            {/* Chat Window */}
            {isOpen && (
                <div
                    className={`fixed bottom-6 right-6 w-96 bg-white rounded-2xl shadow-2xl border border-gray-200 z-50 transition-all duration-200 ${isMinimized ? 'h-16' : 'h-[32rem]'
                        }`}
                >
                    {/* Header */}
                    <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-blue-600 text-white rounded-t-2xl">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                                <Bot size={18} />
                            </div>
                            <div>
                                <h3 className="font-semibold text-sm">Laptop Assistant</h3>
                                <p className="text-xs text-blue-100">Online</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={toggleMinimize}
                                className="p-1 hover:bg-blue-500 rounded"
                                aria-label={isMinimized ? "Maximize chat" : "Minimize chat"}
                            >
                                {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
                            </button>
                            <button
                                onClick={toggleChat}
                                className="p-1 hover:bg-blue-500 rounded"
                                aria-label="Close chat"
                            >
                                <X size={16} />
                            </button>
                        </div>
                    </div>

                    {!isMinimized && (
                        <>
                            {/* Messages */}
                            <div className="flex-1 overflow-y-auto p-4 space-y-4 h-80">
                                {messages.map((message) => (
                                    <div
                                        key={message.id}
                                        className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                    >
                                        {message.role === 'assistant' && (
                                            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                                                <Bot size={16} className="text-blue-600" />
                                            </div>
                                        )}
                                        <div
                                            className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl text-sm ${message.role === 'user'
                                                ? 'bg-blue-600 text-white rounded-br-md'
                                                : 'bg-gray-100 text-gray-900 rounded-bl-md'
                                                }`}
                                        >
                                            <p className="whitespace-pre-wrap">{message.content}</p>
                                            <p className={`text-xs mt-1 ${message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                                                }`}>
                                                {formatTime(message.timestamp)}
                                            </p>
                                        </div>
                                        {message.role === 'user' && (
                                            <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                                                <User size={16} className="text-gray-600" />
                                            </div>
                                        )}
                                    </div>
                                ))}

                                {isLoading && (
                                    <div className="flex gap-3 justify-start">
                                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                                            <Bot size={16} className="text-blue-600" />
                                        </div>
                                        <div className="bg-gray-100 px-4 py-2 rounded-2xl rounded-bl-md">
                                            <div className="flex space-x-1">
                                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                                            </div>
                                        </div>
                                    </div>
                                )}

                                <div ref={messagesEndRef} />
                            </div>

                            {/* Quick Actions */}
                            <div className="px-4 py-2 border-t border-gray-100">
                                <div className="flex gap-2 flex-wrap">
                                    <button
                                        onClick={() => setInputMessage("What laptops do you recommend for under $1000?")}
                                        className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-full text-gray-700 transition-colors"
                                    >
                                        Budget recommendations
                                    </button>
                                    <button
                                        onClick={() => setInputMessage("Compare Lenovo vs HP laptops")}
                                        className="text-xs bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-full text-gray-700 transition-colors"
                                    >
                                        Brand comparison
                                    </button>
                                    <button
                                        onClick={clearChat}
                                        className="text-xs text-gray-500 hover:text-gray-700 px-2 py-1 transition-colors"
                                    >
                                        Clear chat
                                    </button>
                                </div>
                            </div>

                            {/* Input */}
                            <div className="p-4 border-t border-gray-200">
                                <div className="flex gap-2">
                                    <input
                                        ref={inputRef}
                                        type="text"
                                        value={inputMessage}
                                        onChange={(e) => setInputMessage(e.target.value)}
                                        onKeyPress={handleKeyPress}
                                        placeholder="Ask about laptops..."
                                        className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm text-gray-900 placeholder-gray-500"
                                        disabled={isLoading}
                                    />
                                    <button
                                        onClick={sendMessage}
                                        disabled={!inputMessage.trim() || isLoading}
                                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
                                        aria-label="Send message"
                                    >
                                        <Send size={16} />
                                    </button>
                                </div>
                                {error && (
                                    <p className="text-red-500 text-xs mt-2">{error}</p>
                                )}
                            </div>
                        </>
                    )}
                </div>
            )}
        </>
    );
}
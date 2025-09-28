'use client';

import { ArrowLeft, Check, Star, Truck, Shield, ChevronDown, ChevronUp, Cpu, HardDrive, Monitor, Zap, ExternalLink, MessageSquare } from 'lucide-react';
import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Image from 'next/image';
import { getLaptopById } from '@/lib/api';
import { LaptopDetail, QuestionsAnswer } from '@/lib/types';

export default function LaptopDetailPage() {
    const params = useParams();
    const router = useRouter();
    const laptopId = Number(params.id);

    const [laptop, setLaptop] = useState<LaptopDetail | null>(null);
    const [questionsAnswers, setQuestionsAnswers] = useState<QuestionsAnswer[]>([]);
    const [selectedConfig, setSelectedConfig] = useState(0);
    const [showAllConfigs, setShowAllConfigs] = useState(false);
    const [showAllSpecs, setShowAllSpecs] = useState(false);
    const [showAllReviews, setShowAllReviews] = useState(false);
    const [showAllQA, setShowAllQA] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!laptopId) return;

        async function loadLaptopDetails() {
            try {
                const data = await getLaptopById(laptopId);
                setLaptop(data);

                // Fetch Q&A data
                const qaResponse = await fetch(`http://localhost:8000/laptops/${laptopId}/questions`);
                if (qaResponse.ok) {
                    const qaData = await qaResponse.json();
                    setQuestionsAnswers(qaData);
                }
            } catch (_err) {
                setError(`Failed to load laptop details: ${_err}`);
            } finally {
                setIsLoading(false);
            }
        }
        loadLaptopDetails();
    }, [laptopId]);

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-gray-600">Loading laptop details...</div>
            </div>
        );
    }

    if (error || !laptop) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-red-600">{error || 'Laptop not found.'}</div>
            </div>
        );
    }

    const currentPrice = laptop.price_snapshots[selectedConfig];
    const avgRating = laptop.reviews.length > 0
        ? laptop.reviews.reduce((sum, review) => sum + (review.rating || 0), 0) / laptop.reviews.length
        : 0;
    const reviewCount = laptop.reviews.length;

    // Group specifications by category
    const groupedSpecs = laptop.specifications.reduce((acc, spec) => {
        const category = spec.category || "General";
        if (!acc[category]) {
            acc[category] = [];
        }
        acc[category].push(spec);
        return acc;
    }, {} as Record<string, typeof laptop.specifications>);

    const getAvailabilityColor = (status: string) => {
        switch (status) {
            case 'In Stock': return 'text-green-600';
            case 'Limited Stock': return 'text-yellow-600';
            default: return 'text-red-600';
        }
    };

    const getAvailabilityBg = (status: string) => {
        switch (status) {
            case 'In Stock': return 'bg-green-50 border-green-200';
            case 'Limited Stock': return 'bg-yellow-50 border-yellow-200';
            default: return 'bg-red-50 border-red-200';
        }
    };

    // Get icon for specification category
    const getSpecIcon = (category: string) => {
        const cat = category.toLowerCase();
        if (cat.includes('processor') || cat.includes('cpu')) return <Cpu className="w-5 h-5 text-blue-600" />;
        if (cat.includes('memory') || cat.includes('ram')) return <HardDrive className="w-5 h-5 text-green-600" />;
        if (cat.includes('storage') || cat.includes('ssd') || cat.includes('disk')) return <HardDrive className="w-5 h-5 text-purple-600" />;
        if (cat.includes('display') || cat.includes('screen')) return <Monitor className="w-5 h-5 text-orange-600" />;
        if (cat.includes('graphics') || cat.includes('gpu')) return <Zap className="w-5 h-5 text-red-600" />;
        if (cat.includes('connectivity') || cat.includes('port')) return <Shield className="w-5 h-5 text-indigo-600" />;
        return <Shield className="w-5 h-5 text-gray-600" />;
    };

    // Show configurations, reviews, and Q&A with limits
    const displayedConfigs = showAllConfigs ? laptop.price_snapshots : laptop.price_snapshots.slice(0, 3);
    const specCategories = Object.keys(groupedSpecs);
    const displayedSpecCategories = showAllSpecs ? specCategories : specCategories.slice(0, 4);
    const displayedReviews = showAllReviews ? laptop.reviews : laptop.reviews.slice(0, 2);
    const displayedQA = showAllQA ? questionsAnswers : questionsAnswers.slice(0, 3);

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header with back button */}
            <div className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 py-4">
                    <button
                        onClick={() => router.back()}
                        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
                    >
                        <ArrowLeft size={20} />
                        <span>Back to laptops</span>
                    </button>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                    {/* Left: Image */}
                    <div className="space-y-4">
                        <div className="bg-white rounded-2xl p-8 shadow-sm">
                            <Image
                                src={laptop.image_url || '/placeholder-laptop.jpg'}
                                alt={laptop.full_model_name}
                                width={600}
                                height={400}
                                className="w-full h-96 object-cover rounded-lg"
                            />
                        </div>
                    </div>

                    {/* Right: Product Info */}
                    <div className="space-y-6">
                        {/* Brand and Title */}
                        <div>
                            <p className="text-sm text-gray-500 uppercase tracking-wider">{laptop.brand}</p>
                            <h1 className="text-3xl font-bold text-gray-900 mt-1">{laptop.full_model_name}</h1>
                            <p className="text-lg text-gray-600 mt-2">
                                {laptop.brand === 'Lenovo' ? 'ThinkPad Family' : 'ProBook Family'}
                            </p>
                        </div>

                        {/* Price and Rating */}
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="text-4xl font-bold text-blue-600">
                                    {currentPrice?.price ? `$${currentPrice.price.toFixed(2)}` : 'Price on Request'}
                                    <span className="text-lg text-gray-500 ml-2">USD</span>
                                </div>
                                <div className="flex items-center gap-4 mt-2">
                                    <span className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-medium">
                                        Save $300
                                    </span>
                                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                                        Business Discount
                                    </span>
                                </div>
                            </div>
                        </div>

                        {/* Availability and Shipping */}
                        <div className="grid grid-cols-2 gap-4">
                            <div className="flex items-center gap-2">
                                <Check className={`w-5 h-5 ${getAvailabilityColor(currentPrice?.availability_status || '')}`} />
                                <div>
                                    <p className="font-medium text-gray-900">Availability</p>
                                    <p className={`text-sm ${getAvailabilityColor(currentPrice?.availability_status || '')}`}>
                                        {currentPrice?.availability_status || 'Contact for availability'}
                                    </p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <Truck className="w-5 h-5 text-blue-600" />
                                <div>
                                    <p className="font-medium text-gray-900">Shipping</p>
                                    <p className="text-sm text-gray-600">2-3 business days</p>
                                </div>
                            </div>
                        </div>

                        {/* Configuration Selection */}
                        {laptop.price_snapshots.length > 0 && (
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 mb-4">Choose Configuration</h3>
                                <div className="space-y-3">
                                    {displayedConfigs.map((config, index) => (
                                        <div
                                            key={index}
                                            onClick={() => setSelectedConfig(index)}
                                            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${selectedConfig === index
                                                ? 'border-blue-500 bg-blue-50'
                                                : `border-gray-200 hover:border-gray-300 ${getAvailabilityBg(config.availability_status || '')}`
                                                }`}
                                        >
                                            <div className="flex justify-between items-center">
                                                <div>
                                                    <p className="font-medium text-gray-900">
                                                        {config.configuration_summary || 'Standard Configuration'}
                                                    </p>
                                                    <p className={`text-sm ${getAvailabilityColor(config.availability_status || '')}`}>
                                                        {config.availability_status || 'Contact for availability'}
                                                    </p>
                                                </div>
                                                <div className="text-right">
                                                    <p className="text-xl font-bold text-gray-900">
                                                        {config.price ? `$${config.price.toFixed(2)}` : 'Contact for Price'}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    ))}

                                    {laptop.price_snapshots.length > 3 && (
                                        <button
                                            onClick={() => setShowAllConfigs(!showAllConfigs)}
                                            className="w-full p-3 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50 flex items-center justify-center gap-2"
                                        >
                                            {showAllConfigs ? (
                                                <>
                                                    <ChevronUp size={16} />
                                                    Show Less Options
                                                </>
                                            ) : (
                                                <>
                                                    <ChevronDown size={16} />
                                                    Show {laptop.price_snapshots.length - 3} More Options
                                                </>
                                            )}
                                        </button>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Specifications Section */}
                <div className="mt-16 bg-white rounded-2xl p-8 shadow-sm">
                    <div className="flex items-center justify-between mb-8">
                        <h2 className="text-2xl font-bold text-gray-900">Specifications</h2>
                        <a
                            href={laptop.pdf_spec_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 text-blue-600 hover:text-blue-800 text-sm font-medium"
                        >
                            <ExternalLink size={16} />
                            View Full PDF Specifications
                        </a>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {displayedSpecCategories.map((category) => (
                            <div key={category} className="space-y-3">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                        {getSpecIcon(category)}
                                    </div>
                                    <h3 className="font-semibold text-gray-900">{category}</h3>
                                </div>
                                <div className="space-y-2">
                                    {groupedSpecs[category].slice(0, 2).map((spec, index) => (
                                        <div key={index}>
                                            <p className="text-sm text-gray-600">{spec.specification_name}</p>
                                            <p className="text-sm text-gray-800 font-medium">
                                                {spec.specification_value.length > 50
                                                    ? `${spec.specification_value.substring(0, 50)}...`
                                                    : spec.specification_value}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>

                    {specCategories.length > 4 && (
                        <div className="mt-6 text-center">
                            <button
                                onClick={() => setShowAllSpecs(!showAllSpecs)}
                                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50 flex items-center gap-2 mx-auto"
                            >
                                {showAllSpecs ? (
                                    <>
                                        <ChevronUp size={16} />
                                        Show Less Specifications
                                    </>
                                ) : (
                                    <>
                                        <ChevronDown size={16} />
                                        Show All Specifications
                                    </>
                                )}
                            </button>
                        </div>
                    )}
                </div>

                {/* Reviews and Q&A Section */}
                <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Customer Reviews */}
                    <div className="bg-white rounded-2xl p-8 shadow-sm">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-bold text-gray-900">Customer Reviews</h2>
                            {laptop.reviews.length > 2 && (
                                <button
                                    onClick={() => setShowAllReviews(!showAllReviews)}
                                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                                >
                                    {showAllReviews ? 'Show Less' : `View All ${reviewCount} Reviews`}
                                </button>
                            )}
                        </div>
                        <div className="space-y-4">
                            {reviewCount > 0 ? (
                                <>
                                    <div className="flex items-center gap-2">
                                        <div className="flex">
                                            {[...Array(5)].map((_, i) => (
                                                <Star
                                                    key={i}
                                                    size={20}
                                                    className={i < Math.floor(avgRating) ? "text-yellow-400 fill-current" : "text-gray-300"}
                                                />
                                            ))}
                                        </div>
                                        <span className="text-lg font-semibold">{avgRating.toFixed(1)}</span>
                                        <span className="text-gray-600">({reviewCount} reviews)</span>
                                    </div>

                                    <div className="space-y-3">
                                        {displayedReviews.map((review, index) => (
                                            <div key={index} className="border border-gray-200 rounded-lg p-4">
                                                <div className="flex items-center justify-between mb-2">
                                                    <span className="font-medium text-gray-900">
                                                        {review.review_title || 'Customer Review'}
                                                    </span>
                                                    <div className="flex">
                                                        {[...Array(5)].map((_, i) => (
                                                            <Star
                                                                key={i}
                                                                size={16}
                                                                className={i < (review.rating || 0) ? "text-yellow-400 fill-current" : "text-gray-300"}
                                                            />
                                                        ))}
                                                    </div>
                                                </div>
                                                <p className="text-sm text-gray-600 italic">
                                                    by {review.reviewer_name || 'Anonymous'}
                                                </p>
                                                <p className="text-sm text-gray-800 mt-2">
                                                    {showAllReviews || !review.review_text || review.review_text.length <= 150
                                                        ? review.review_text
                                                        : `${review.review_text.substring(0, 150)}...`}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </>
                            ) : (
                                <p className="text-gray-500">No reviews available yet.</p>
                            )}
                        </div>
                    </div>

                    {/* Questions & Answers */}
                    <div className="bg-white rounded-2xl p-8 shadow-sm">
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-xl font-bold text-gray-900">Questions & Answers</h2>
                            {questionsAnswers.length > 3 && (
                                <button
                                    onClick={() => setShowAllQA(!showAllQA)}
                                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                                >
                                    {showAllQA ? 'Show Less' : `View All ${questionsAnswers.length} Q&As`}
                                </button>
                            )}
                        </div>
                        <div className="space-y-4">
                            {displayedQA.length > 0 ? (
                                displayedQA.map((qa, index) => (
                                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                                        <div className="flex items-start gap-3 mb-3">
                                            <MessageSquare className="w-5 h-5 text-blue-600 mt-1 flex-shrink-0" />
                                            <div className="flex-1">
                                                <p className="font-medium text-gray-900 mb-1">
                                                    {qa.question_text}
                                                </p>
                                                <p className="text-xs text-gray-500">
                                                    by {qa.asker_name || 'Anonymous'}
                                                </p>
                                            </div>
                                        </div>
                                        {qa.answer_text && (
                                            <div className="ml-8 bg-gray-50 p-3 rounded-lg">
                                                <p className="text-sm text-gray-800 mb-1">
                                                    {qa.answer_text}
                                                </p>
                                                <p className="text-xs text-gray-500">
                                                    answered by {qa.answerer_name || 'Anonymous'}
                                                </p>
                                            </div>
                                        )}
                                    </div>
                                ))
                            ) : (
                                <p className="text-gray-500">No questions asked yet.</p>
                            )}
                        </div>
                    </div>
                </div>

                {/* Price History Section */}
                <div className="mt-8 bg-white rounded-2xl p-8 shadow-sm">
                    <h2 className="text-xl font-bold text-gray-900 mb-6">Price History</h2>
                    <div className="space-y-4">
                        <p className="text-gray-600">Price trend over the last few months.</p>
                        <div className="h-32 bg-gradient-to-r from-blue-100 to-purple-100 rounded-lg flex items-center justify-center">
                            <p className="text-gray-500">Chart visualization coming soon</p>
                        </div>
                        <div className="text-sm text-gray-600">
                            <p>Current price: {currentPrice?.price ? `$${currentPrice.price.toFixed(2)}` : 'Contact for pricing'}</p>
                            <p>Configurations available: {laptop.price_snapshots.length}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
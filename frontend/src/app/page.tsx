'use client';

import { useEffect, useState } from 'react';
import { Search, Filter, ChevronDown, Star, X } from 'lucide-react';
import { ProductCard } from "@/components/domain/ProductCard";
import { getAllLaptops } from '@/lib/api';
import { LaptopSimple } from '@/lib/types';

export default function HomePage() {
  // State management
  const [laptops, setLaptops] = useState<LaptopSimple[]>([]);
  const [filteredLaptops, setFilteredLaptops] = useState<LaptopSimple[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBrand, setSelectedBrand] = useState('');
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 2000]);
  const [minRating, setMinRating] = useState(0);
  const [showFilters, setShowFilters] = useState(false);

  // Load laptops
  useEffect(() => {
    async function loadLaptops() {
      try {
        const data = await getAllLaptops();
        setLaptops(data);
        setFilteredLaptops(data);
      } catch (err) {
        setError('Failed to load laptops. Please ensure the API server is running.');
      } finally {
        setIsLoading(false);
      }
    }

    loadLaptops();
  }, []);

  // Apply filters
  useEffect(() => {
    let filtered = laptops;

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(laptop =>
        laptop.full_model_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        laptop.brand.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Brand filter
    if (selectedBrand) {
      filtered = filtered.filter(laptop => laptop.brand === selectedBrand);
    }

    // Price filter
    filtered = filtered.filter(laptop => {
      const price = laptop.latest_price || 0;
      return price >= priceRange[0] && price <= priceRange[1];
    });

    // Rating filter
    if (minRating > 0) {
      filtered = filtered.filter(laptop => (laptop.average_rating || 0) >= minRating);
    }

    setFilteredLaptops(filtered);
  }, [laptops, searchQuery, selectedBrand, priceRange, minRating]);

  // Get unique brands
  const brands = [...new Set(laptops.map(laptop => laptop.brand))];

  // Clear all filters
  const clearFilters = () => {
    setSearchQuery('');
    setSelectedBrand('');
    setPriceRange([0, 2000]);
    setMinRating(0);
  };

  const hasActiveFilters = searchQuery || selectedBrand || priceRange[0] > 0 || priceRange[1] < 2000 || minRating > 0;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-gray-600">Loading laptops...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 mb-4">{error}</div>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Business Laptops</h1>
              <p className="text-gray-600 mt-1">
                Compare {laptops.length} professional laptops from top brands
              </p>
            </div>

            {/* Search Bar */}
            <div className="relative max-w-md w-full">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search laptops by model or brand..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-500"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <div className="lg:w-64 space-y-6">
            {/* Mobile filter toggle */}
            <div className="lg:hidden">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center gap-2 w-full px-4 py-2 border border-gray-300 rounded-lg bg-white"
              >
                <Filter size={20} />
                <span>Filters</span>
                <ChevronDown className={`ml-auto transform transition-transform ${showFilters ? 'rotate-180' : ''}`} size={20} />
              </button>
            </div>

            {/* Filter content */}
            <div className={`space-y-6 ${showFilters ? 'block' : 'hidden'} lg:block`}>
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="font-semibold text-gray-900">Filters</h2>
                  {hasActiveFilters && (
                    <button
                      onClick={clearFilters}
                      className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                    >
                      <X size={16} />
                      Clear all
                    </button>
                  )}
                </div>

                {/* Brand Filter */}
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-gray-700">Brand</label>
                  <select
                    value={selectedBrand}
                    onChange={(e) => setSelectedBrand(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                  >
                    <option value="">All Brands</option>
                    {brands.map(brand => (
                      <option key={brand} value={brand}>{brand}</option>
                    ))}
                  </select>
                </div>

                {/* Price Range */}
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-gray-700">Price Range</label>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        placeholder="Min"
                        value={priceRange[0]}
                        onChange={(e) => setPriceRange([Number(e.target.value), priceRange[1]])}
                        className="w-20 px-2 py-1 border border-gray-300 rounded text-sm text-gray-900 placeholder-gray-500"
                      />
                      <span className="text-gray-700">to</span>
                      <input
                        type="number"
                        placeholder="Max"
                        value={priceRange[1]}
                        onChange={(e) => setPriceRange([priceRange[0], Number(e.target.value)])}
                        className="w-20 px-2 py-1 border border-gray-300 rounded text-sm text-gray-900 placeholder-gray-500"
                      />
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="2000"
                      step="50"
                      value={priceRange[1]}
                      onChange={(e) => setPriceRange([priceRange[0], Number(e.target.value)])}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>$0</span>
                      <span>$2000+</span>
                    </div>
                  </div>
                </div>

                {/* Rating Filter */}
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-gray-700">Minimum Rating</label>
                  <div className="space-y-2">
                    {[4, 3, 2, 1].map(rating => (
                      <label key={rating} className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="radio"
                          name="rating"
                          value={rating}
                          checked={minRating === rating}
                          onChange={(e) => setMinRating(Number(e.target.value))}
                          className="text-blue-600"
                        />
                        <div className="flex items-center gap-1">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              size={16}
                              className={i < rating ? "text-yellow-400 fill-current" : "text-gray-300"}
                            />
                          ))}
                          <span className="text-sm text-gray-600">& up</span>
                        </div>
                      </label>
                    ))}
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="rating"
                        value={0}
                        checked={minRating === 0}
                        onChange={(e) => setMinRating(Number(e.target.value))}
                        className="text-blue-600"
                      />
                      <span className="text-sm text-gray-600">All ratings</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            {/* Results header */}
            <div className="flex items-center justify-between mb-6">
              <div className="text-gray-600">
                {filteredLaptops.length} of {laptops.length} laptops
                {hasActiveFilters && (
                  <span className="ml-2 text-sm">
                    (filtered)
                  </span>
                )}
              </div>

              {/* Sort options could go here */}
              <select className="px-3 py-2 border border-gray-300 rounded-md text-sm">
                <option>Sort by relevance</option>
                <option>Price: Low to High</option>
                <option>Price: High to Low</option>
                <option>Highest rated</option>
                <option>Newest first</option>
              </select>
            </div>

            {/* Laptop Grid */}
            {filteredLaptops.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {filteredLaptops.map((laptop) => (
                  <ProductCard
                    key={laptop.id}
                    id={laptop.id}
                    brand={laptop.brand}
                    modelName={laptop.full_model_name}
                    imageUrl={laptop.image_url || '/placeholder-laptop.jpg'}
                    price={laptop.latest_price || 0}
                    average_rating={laptop.average_rating || 0}
                    reviewCount={laptop.review_count || 0}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-gray-500 mb-4">No laptops found matching your criteria</div>
                <button
                  onClick={clearFilters}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Clear Filters
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
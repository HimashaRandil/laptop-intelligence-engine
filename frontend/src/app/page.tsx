// in src/app/page.tsx
'use client'; // This is required to use hooks like useState and useEffect

import { useEffect, useState } from 'react';
import { ProductCard } from "@/components/domain/ProductCard";
import { getAllLaptops } from '@/lib/api';
import { LaptopSimple } from '@/lib/types';

export default function HomePage() {
  // 1. State Management: We create variables to store our data.
  const [laptops, setLaptops] = useState<LaptopSimple[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 2. Data Fetching: This effect runs once when the page loads.
  useEffect(() => {
    async function loadLaptops() {
      try {
        // We call our API function to get the live data
        const data = await getAllLaptops();
        setLaptops(data);
      } catch (err) {
        setError('Failed to load laptops. Please ensure the API server is running.');
      } finally {
        setIsLoading(false);
      }
    }

    loadLaptops();
  }, []); // The empty array [] ensures this runs only once.

  // 3. Conditional UI: Show a loading or error message.
  if (isLoading) {
    return <div className="text-center p-10 text-white">Loading laptops...</div>;
  }

  if (error) {
    return <div className="text-center p-10 text-red-500">{error}</div>;
  }

  // 4. Dynamic Rendering: Map over the live data from the state.
  return (
    <main className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6 text-white">Laptops</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {laptops.map((laptop) => (
          <ProductCard
            key={laptop.id}
            id={laptop.id}
            brand={laptop.brand}
            modelName={laptop.full_model_name}
            imageUrl={laptop.image_url || '/placeholder1.jpg'}
            price={laptop.latest_price || 0}
            average_rating={laptop.average_rating || 0}
            reviewCount={laptop.reviewCount || 0}
          />
        ))}
      </div>
    </main>
  );
}
// in src/app/laptops/[id]/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation'; // 1. Import the useParams hook
import { getLaptopById } from '@/lib/api';
import { LaptopDetail } from '@/lib/types';
import Image from 'next/image';
import { SpecTable } from '@/components/domain/SpecTable';
import { PriceList } from '@/components/domain/PriceList';
import { ReviewList } from '@/components/domain/ReviewList';

// 2. Remove 'params' from the function arguments
export default function LaptopDetailPage() {
    const params = useParams(); // 3. Call the hook to get the params
    const laptopId = Number(params.id); // 4. Get the id and convert to a number

    const [laptop, setLaptop] = useState<LaptopDetail | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        // Make sure we have a valid ID before fetching
        if (!laptopId) return;

        async function loadLaptopDetails() {
            try {
                const data = await getLaptopById(laptopId); // Use the id from the hook
                setLaptop(data);
            } catch (err) {
                setError('Failed to load laptop details.');
            } finally {
                setIsLoading(false);
            }
        }
        loadLaptopDetails();
    }, [laptopId]); // 5. Use the id from the hook in the dependency array

    if (isLoading) {
        return <div className="text-center p-10 text-white">Loading details...</div>;
    }

    if (error || !laptop) {
        return <div className="text-center p-10 text-red-500">{error || 'Laptop not found.'}</div>;
    }

    // ... (the rest of your return statement stays the same)
    return (
        <main className="container mx-auto p-4 text-white">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Left Column: Image and Title */}
                <div className="md:col-span-1">
                    <Image
                        src={laptop.image_url || '/placeholder1.jpg'}
                        alt={laptop.full_model_name}
                        width={600}
                        height={400}
                        className="rounded-lg object-cover w-full sticky top-4"
                    />
                    <div className="mt-4">
                        <p className="text-lg text-gray-400">{laptop.brand}</p>
                        <h1 className="text-3xl font-bold">{laptop.full_model_name}</h1>
                    </div>
                </div>

                {/* Right Column: Specs, Prices, and Reviews */}
                <div className="md:col-span-2 space-y-8">
                    {/* 3. Add the PriceList and ReviewList components */}
                    <PriceList prices={laptop.price_snapshots} />
                    <ReviewList reviews={laptop.reviews} />
                    <SpecTable specifications={laptop.specifications} />
                </div>
            </div>
        </main>
    );
}
// in src/components/domain/ProductCard.tsx
import { Card } from '@/components/ui/Card';
import Image from 'next/image';
import Link from 'next/link'; // 
import { Star } from 'lucide-react';

// Define the "shape" of the data this component expects
interface ProductCardProps {
    id: number;
    imageUrl: string;
    brand: string;
    modelName: string;
    price: number;
    average_rating: number | null;
    review_count: number | null;
}

export function ProductCard(props: ProductCardProps) {
    return (
        <Link href={`/laptops/${props.id}`} className="block hover:scale-105 transition-transform duration-200">
            <Card>
                <div className="relative">
                    <Image
                        src={props.imageUrl || '/placeholder1.jpg'} // Use a placeholder if the API provides no image
                        alt={props.modelName}
                        width={400}
                        height={300}
                        className="object-cover w-full h-48"
                    />
                </div>
                <div className="p-4 flex flex-col">
                    <p className="text-sm text-gray-500">{props.brand}</p>
                    <h3 className="text-lg font-semibold text-gray-800 truncate h-14">{props.modelName}</h3>

                    <div className="flex items-center justify-between mt-4">
                        <p className="text-xl font-bold text-gray-900">
                            {props.price ? `$${props.price.toFixed(2)}` : 'N/A'}
                        </p>
                        <div className="flex items-center gap-1 text-sm text-gray-600">
                            <Star size={16} className="text-yellow-500" />
                            <span>
                                {props.average_rating ? props.average_rating.toFixed(1) : 'New'} ({props.reviewCount || 0})
                            </span>
                        </div>
                    </div>
                </div>
            </Card>
        </Link>
    );
}
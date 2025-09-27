import { PriceSnapshot } from "@/lib/types";
import { Card } from "../ui/Card";
import { Tag } from 'lucide-react';

interface PriceListProps {
    prices: PriceSnapshot[];
}

export function PriceList({ prices }: PriceListProps) {
    if (!prices || prices.length === 0) {
        return <p className="text-gray-400">No pricing information available.</p>;
    }

    return (
        <div>
            <h2 className="text-2xl font-semibold mb-4 text-white">Buying Options</h2>
            <div className="space-y-4">
                {prices.map((price, index) => (
                    <Card key={index} className="bg-gray-800 border-gray-700 p-4 flex justify-between items-center">
                        <div>
                            <p className="font-medium text-gray-300">{price.configuration_summary || 'Base Model'}</p>
                            <p className={`text-sm ${price.availability_status === 'In Stock' ? 'text-green-400' : 'text-yellow-400'}`}>
                                {price.availability_status || 'Availability unknown'}
                            </p>
                        </div>
                        <div className="text-right">
                            <p className="text-xl font-bold text-white">
                                {price.price ? `$${price.price.toFixed(2)}` : 'N/A'}
                            </p>
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    );
}
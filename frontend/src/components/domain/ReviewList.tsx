// in src/components/domain/ReviewList.tsx
import { Review } from "@/lib/types";
import { Card } from "../ui/Card";
import { Star } from "lucide-react";

interface ReviewListProps {
    reviews: Review[];
}

// A helper component to render the star rating
const StarRating = ({ rating }: { rating: number }) => (
    <div className="flex items-center">
        {[...Array(5)].map((_, i) => (
            <Star
                key={i}
                size={16}
                className={i < rating ? "text-yellow-500 fill-current" : "text-gray-600"}
            />
        ))}
    </div>
);

export function ReviewList({ reviews }: ReviewListProps) {
    if (!reviews || reviews.length === 0) {
        return <p className="text-gray-400">No reviews available for this product yet.</p>;
    }

    return (
        <div>
            <h2 className="text-2xl font-semibold mb-4 text-white">Customer Reviews</h2>
            <div className="space-y-4">
                {reviews.map((review, index) => (
                    <Card key={index} className="bg-gray-800 border-gray-700 p-4">
                        <div className="flex items-center justify-between mb-2">
                            <p className="font-semibold text-gray-300">{review.reviewer_name || 'Anonymous'}</p>
                            {review.rating && <StarRating rating={review.rating} />}
                        </div>
                        <h4 className="font-medium text-gray-400 mb-1">{review.review_title}</h4>
                        <p className="text-sm text-gray-400">{review.review_text}</p>
                    </Card>
                ))}
            </div>
        </div>
    );
}
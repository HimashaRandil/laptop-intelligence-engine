import { Specification } from "@/lib/types";
import { Card } from "../ui/Card";

interface SpecTableProps {
    specifications: Specification[];
}

// A helper function to group specs by their category
function groupSpecsByCategory(specs: Specification[]): Record<string, Specification[]> {
    return specs.reduce((acc, spec) => {
        const category = spec.category || "General";
        if (!acc[category]) {
            acc[category] = [];
        }
        acc[category].push(spec);
        return acc;
    }, {} as Record<string, Specification[]>);
}

export function SpecTable({ specifications }: SpecTableProps) {
    const groupedSpecs = groupSpecsByCategory(specifications);

    return (
        <div className="space-y-6">
            {Object.entries(groupedSpecs).map(([category, specs]) => (
                <div key={category}>
                    <h3 className="text-xl font-semibold mb-3 text-white">{category}</h3>
                    <Card className="bg-gray-800 border-gray-700">
                        <table className="w-full text-sm text-left">
                            <tbody className="divide-y divide-gray-700">
                                {specs.map((spec, index) => (
                                    <tr key={index}>
                                        <th scope="row" className="px-4 py-3 font-medium text-gray-300 w-1/3">
                                            {spec.specification_name}
                                        </th>
                                        <td className="px-4 py-3 text-gray-400">
                                            {/* We will add logic here later to nicely display the structured_value */}
                                            {spec.specification_value}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </Card>
                </div>
            ))}
        </div>
    );
}
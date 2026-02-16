import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ParsingStats } from "../../types/logistics";

interface ParsingStatsCardProps {
    stats: ParsingStats;
}

export function ParsingStatsCard({ stats }: ParsingStatsCardProps) {
    return (
        <Card className="p-6 border-2 hover:shadow-md transition-all">
            <h3 className="text-lg font-bold mb-4">Parsing Statistics</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="p-3 bg-secondary rounded-lg">
                    <p className="text-xs text-muted-foreground">Total Elements</p>
                    <p className="text-xl font-bold">{stats.total_elements}</p>
                </div>
                <div className="p-3 bg-green-100 dark:bg-green-950 rounded-lg">
                    <p className="text-xs text-muted-foreground">Valid Parcels</p>
                    <p className="text-xl font-bold text-green-600">{stats.valid_parcels}</p>
                </div>
                <div className="p-3 bg-orange-100 dark:bg-orange-950 rounded-lg">
                    <p className="text-xs text-muted-foreground">Duplicates</p>
                    <p className="text-xl font-bold text-orange-600">{stats.duplicates_removed}</p>
                </div>
                <div className="p-3 bg-red-100 dark:bg-red-950 rounded-lg">
                    <p className="text-xs text-muted-foreground">Skipped</p>
                    <p className="text-xl font-bold text-red-600">{stats.skipped_invalid}</p>
                </div>
            </div>

            {stats.removed_parcels.length > 0 && (
                <div>
                    <h4 className="text-sm font-semibold mb-2">Removed Items Detail</h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto pr-2">
                        {stats.removed_parcels.map((removed, idx) => (
                            <div key={idx} className="flex justify-between items-center text-xs p-2 bg-muted rounded">
                                <div>
                                    <span className="font-mono font-bold mr-2">{removed.parcel_id}</span>
                                    <span className="text-muted-foreground">{removed.details}</span>
                                </div>
                                <Badge variant="outline" className="text-[10px] uppercase">
                                    {removed.reason.replace("_", " ")}
                                </Badge>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </Card>
    );
}

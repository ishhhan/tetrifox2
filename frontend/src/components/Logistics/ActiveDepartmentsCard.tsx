import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { X, Trash2 } from "lucide-react";
import { DepartmentRule } from "../../types/logistics";

interface ActiveDepartmentsCardProps {
    departments: DepartmentRule[];
    onRemove: (index: number) => void;
    onClearAll: () => void;
}

export function ActiveDepartmentsCard({ departments, onRemove, onClearAll }: ActiveDepartmentsCardProps) {
    return (
        <Card className="p-6 border-2 hover:shadow-lg transition-all">
            <div className="flex justify-between items-center mb-4">
                <h3 className="font-bold text-lg">Active Departments ({departments.length})</h3>
                {departments.length > 0 && (
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={onClearAll}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950 p-2 h-auto text-xs"
                    >
                        <Trash2 className="w-3 h-3 mr-1" />
                        Clear All
                    </Button>
                )}
            </div>

            <div className="space-y-2 max-h-[300px] overflow-y-auto pr-2">
                {departments.length === 0 ? (
                    <p className="text-muted-foreground text-sm">No departments added yet</p>
                ) : (
                    departments.map((dept, idx) => {
                        const getUnit = () => {
                            if (dept.field === 'weight') return ' kg';
                            if (dept.field === 'value') return ' €';
                            return '';
                        };

                        return (
                            <div key={idx} className="flex items-center justify-between bg-secondary p-3 rounded">
                                <div className="flex-1">
                                    <p className="font-medium text-sm">{dept.name}</p>
                                    <div className="flex gap-2 mt-1">
                                        <Badge variant="outline" className="text-[10px]">{dept.field}</Badge>
                                        <Badge variant="outline" className="text-[10px]">
                                            {dept.type === "range"
                                                ? `${(dept.min ?? 0).toLocaleString()}${getUnit()} - ${dept.max?.toLocaleString() ?? '∞'}${getUnit()}`
                                                : dept.match_value}
                                        </Badge>
                                    </div>
                                </div>
                                <button onClick={() => onRemove(idx)} className="hover:text-destructive"><X className="w-4 h-4" /></button>
                            </div>
                        );
                    })
                )}
            </div>
        </Card>
    );
}

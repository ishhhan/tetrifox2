import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ArrowUp, ArrowDown, X } from "lucide-react";
import { DepartmentType } from "../../types/logistics";

const FIELD_OPTIONS: { value: DepartmentType; label: string }[] = [
    { value: "weight", label: "Weight" },
    { value: "value", label: "Value" },
    { value: "postal_code", label: "Postal Code" },
    { value: "city", label: "City" },
    { value: "recipient", label: "Recipient" },
];

interface PriorityOrderCardProps {
    priorityOrder: DepartmentType[];
    onAdd: (field: DepartmentType) => void;
    onRemove: (index: number) => void;
    onMoveUp: (index: number) => void;
    onMoveDown: (index: number) => void;
}

export function PriorityOrderCard({
    priorityOrder,
    onAdd,
    onRemove,
    onMoveUp,
    onMoveDown
}: PriorityOrderCardProps) {
    return (
        <Card className="p-6 border-2 hover:shadow-lg transition-all">
            <h3 className="font-bold text-lg mb-4">Preference Order</h3>
            <div className="mb-4">
                <label className="text-sm mb-2 block font-medium">Add to Priority List</label>
                <Select onValueChange={(value) => onAdd(value as DepartmentType)}>
                    <SelectTrigger>
                        <SelectValue placeholder="Select a department..." />
                    </SelectTrigger>
                    <SelectContent>
                        {FIELD_OPTIONS.map((opt) => (
                            <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            <div className="space-y-2">
                {priorityOrder.length === 0 ? (
                    <p className="text-muted-foreground text-sm">No priority set</p>
                ) : (
                    priorityOrder.map((field, idx) => (
                        <div key={idx} className="flex items-center justify-between bg-secondary p-3 rounded group">
                            <Badge variant="outline" className="bg-card">
                                P{idx + 1}: {FIELD_OPTIONS.find((o) => o.value === field)?.label}
                            </Badge>
                            <div className="flex gap-2">
                                <button onClick={() => onMoveUp(idx)} disabled={idx === 0} className="hover:text-primary disabled:opacity-30"><ArrowUp className="w-4 h-4" /></button>
                                <button onClick={() => onMoveDown(idx)} disabled={idx === priorityOrder.length - 1} className="hover:text-primary disabled:opacity-30"><ArrowDown className="w-4 h-4" /></button>
                                <button onClick={() => onRemove(idx)} className="hover:text-destructive"><X className="w-4 h-4" /></button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </Card>
    );
}

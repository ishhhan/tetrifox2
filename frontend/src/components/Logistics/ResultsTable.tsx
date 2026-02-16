import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { ArrowUp, ArrowDown } from "lucide-react";
import { ParcelOutput, SortConfig } from "../../types/logistics";
import { useState, useMemo } from "react";

interface ResultsTableProps {
    data: ParcelOutput[];
}

export function ResultsTable({ data }: ResultsTableProps) {
    const [sortConfig, setSortConfig] = useState<SortConfig>(null);

    const sortedData = useMemo(() => {
        if (!sortConfig) return data;

        const { column, direction } = sortConfig;
        return [...data].sort((a, b) => {
            const getVal = (item: ParcelOutput) => {
                switch (column) {
                    case 'id': return item.parcel_id;
                    case 'recipient': return item.recipient;
                    case 'city': return item.address.city;
                    case 'weight': return item.weight;
                    case 'value': return item.value;
                    default: return '';
                }
            };

            const aVal = getVal(a);
            const bVal = getVal(b);

            if (typeof aVal === 'string') {
                return direction === 'asc' ? aVal.localeCompare(bVal as string) : (bVal as string).localeCompare(aVal);
            }
            return direction === 'asc' ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number);
        });
    }, [data, sortConfig]);

    const requestSort = (column: string) => {
        let direction: 'asc' | 'desc' = 'asc';
        if (sortConfig?.column === column && sortConfig.direction === 'asc') direction = 'desc';
        setSortConfig({ column, direction });
    };

    const SortIcon = ({ column }: { column: string }) => {
        if (sortConfig?.column !== column) return <ArrowUp className="w-3 h-3 opacity-20" />;
        return sortConfig.direction === 'asc' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />;
    };

    return (
        <div className="rounded-md border bg-card">
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead className="cursor-pointer" onClick={() => requestSort('id')}>
                            ID <SortIcon column="id" />
                        </TableHead>
                        <TableHead className="cursor-pointer" onClick={() => requestSort('recipient')}>
                            Recipient <SortIcon column="recipient" />
                        </TableHead>
                        <TableHead className="cursor-pointer" onClick={() => requestSort('city')}>
                            City <SortIcon column="city" />
                        </TableHead>
                        <TableHead className="cursor-pointer" onClick={() => requestSort('weight')}>
                            Weight <SortIcon column="weight" />
                        </TableHead>
                        <TableHead className="cursor-pointer" onClick={() => requestSort('value')}>
                            Value <SortIcon column="value" />
                        </TableHead>
                        <TableHead>Assigned Routes</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {sortedData.map((parcel) => (
                        <TableRow key={parcel.parcel_id}>
                            <TableCell className="font-mono text-xs">{parcel.parcel_id}</TableCell>
                            <TableCell className="font-medium">{parcel.recipient}</TableCell>
                            <TableCell>{parcel.address.city}</TableCell>
                            <TableCell>{parcel.weight.toLocaleString()} kg</TableCell>
                            <TableCell>€{parcel.value.toLocaleString()}</TableCell>
                            <TableCell>
                                <div className="flex flex-wrap items-center gap-1">
                                    {parcel.assigned_route.length > 0 ? (
                                        parcel.assigned_route.map((route, i) => (
                                            <div key={i} className="flex items-center">
                                                {i > 0 && <span className="text-muted-foreground mx-1 text-xs">→</span>}
                                                <Badge variant="secondary" className="text-[10px] px-1 font-mono">
                                                    {route}
                                                </Badge>
                                            </div>
                                        ))
                                    ) : (
                                        <span className="text-xs text-muted-foreground italic">None matched</span>
                                    )}
                                </div>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}

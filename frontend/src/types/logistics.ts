export type DepartmentType = "weight" | "value" | "postal_code" | "city" | "recipient";

export interface DepartmentRule {
    name: string;
    field: DepartmentType;
    type: "range" | "match";
    min?: number;
    max?: number;
    match_value?: string;
}

export interface Address {
    city: string;
    street: string;
    postal_code: string;
}

export interface ParcelOutput {
    parcel_id: string;
    recipient: string;
    weight: number;
    value: number;
    address: Address;
    assigned_route: string[];
}

export interface RemovedParcel {
    parcel_id: string;
    reason: string;
    details: string;
}

export interface ParsingStats {
    total_elements: number;
    valid_parcels: number;
    duplicates_removed: number;
    skipped_invalid: number;
    missing_fields: Record<string, number>;
    duplicate_ids: string[];
    removed_parcels: RemovedParcel[];
}

export interface ProcessResponse {
    status: string;
    total_processed: number;
    data: ParcelOutput[];
    departments?: DepartmentRule[];
    priority_order?: DepartmentType[];
    parsing_stats?: ParsingStats;
}

export interface HistoryEntry {
    id: string;
    timestamp: string;
    total_processed: number;
}

export interface HistoryDetail extends ProcessResponse {
    id: string;
    timestamp: string;
}

export type SortConfig = { column: string; direction: "asc" | "desc" } | null;

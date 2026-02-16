import { useState } from "react";
import { toast } from "sonner";
import { HistoryEntry, ParcelOutput, DepartmentRule, DepartmentType, ParsingStats } from "../types/logistics";
import { api } from "../lib/api";

interface HistoryActions {
    setResults: (data: ParcelOutput[]) => void;
    setDepartments: (data: DepartmentRule[]) => void;
    setPriorityOrder: (data: DepartmentType[]) => void;
    setParsingStats: (data: ParsingStats | null) => void;
}

export function useHistory({ setResults, setDepartments, setPriorityOrder, setParsingStats }: HistoryActions) {
    const [historyList, setHistoryList] = useState<HistoryEntry[]>([]);
    const [historyOpen, setHistoryOpen] = useState(false);
    const [loading, setLoading] = useState(false);

    const fetchHistory = async () => {
        setLoading(true);
        try {
            const data = await api.getHistory();
            setHistoryList(data.history || []);
        } catch (error) {
            toast.error("Failed to load history");
        } finally {
            setLoading(false);
        }
    };

    const loadEntry = async (entryId: string) => {
        try {
            const data = await api.getHistoryEntry(entryId);
            setResults(data.data);
            if (data.departments) setDepartments(data.departments);
            if (data.priority_order) setPriorityOrder(data.priority_order);
            setParsingStats(data.parsing_stats || null);
            setHistoryOpen(false);
            toast.success(`Loaded history entry with ${data.total_processed} parcels`);
        } catch (error) {
            toast.error("Failed to load history entry");
        }
    };

    const deleteEntry = async (entryId: string) => {
        try {
            await api.deleteHistoryEntry(entryId);
            setHistoryList(prev => prev.filter(e => e.id !== entryId));
            toast.success("History entry deleted");
        } catch (error) {
            toast.error("Failed to delete history entry");
        }
    };

    return {
        historyList,
        historyOpen,
        setHistoryOpen,
        loading,
        fetchHistory,
        loadEntry,
        deleteEntry
    };
}

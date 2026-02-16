import { useState } from "react";
import { toast } from "sonner";
import {
    ParcelOutput,
    DepartmentRule,
    DepartmentType,
    ParsingStats
} from "../types/logistics";
import { api } from "../lib/api";

export function useLogistics() {
    const [xmlData, setXmlData] = useState("");
    const [departments, setDepartments] = useState<DepartmentRule[]>([]);
    const [priorityOrder, setPriorityOrder] = useState<DepartmentType[]>([]);
    const [results, setResults] = useState<ParcelOutput[]>([]);
    const [loading, setLoading] = useState(false);
    const [parsingStats, setParsingStats] = useState<ParsingStats | null>(null);

    const handleXmlUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                setXmlData(e.target?.result as string);
                toast.success("XML file loaded");
            };
            reader.readAsText(file);
        }
    };

    const clearXmlData = () => {
        setXmlData("");
        toast.success("XML data cleared");
    };

    const removeDepartment = (index: number) => {
        setDepartments(departments.filter((_, i) => i !== index));
        toast.success("Department removed");
    };

    const addToPriority = (field: DepartmentType) => {
        if (!priorityOrder.includes(field)) {
            setPriorityOrder([...priorityOrder, field]);
            toast.success("Added to priority order");
        } else {
            toast.error("Already in priority order");
        }
    };

    const removePriority = (index: number) => {
        setPriorityOrder(priorityOrder.filter((_, i) => i !== index));
    };

    const movePriorityUp = (index: number) => {
        if (index === 0) return;
        const newOrder = [...priorityOrder];
        [newOrder[index], newOrder[index - 1]] = [newOrder[index - 1], newOrder[index]];
        setPriorityOrder(newOrder);
    };

    const movePriorityDown = (index: number) => {
        if (index === priorityOrder.length - 1) return;
        const newOrder = [...priorityOrder];
        [newOrder[index], newOrder[index + 1]] = [newOrder[index + 1], newOrder[index]];
        setPriorityOrder(newOrder);
    };

    const handleSubmit = async () => {
        if (!xmlData) return toast.error("Please upload an XML file");
        if (departments.length === 0) return toast.error("Please add at least one department");
        if (priorityOrder.length === 0) return toast.error("Please set a priority order");

        setLoading(true);
        try {
            const data = await api.processLogistics({
                xml_data: xmlData,
                departments: departments,
                priority_order: priorityOrder,
            });

            if (data.status === "success") {
                setResults(data.data);
                setParsingStats(data.parsing_stats || null);
                toast.success(`Processed ${data.total_processed} parcels`);
            }
        } catch (data: any) {
            // Handle the detailed error objects we get back from FastAPI
            if (data.detail && Array.isArray(data.detail)) {
                data.detail.forEach((err: any) => toast.error(err.msg.replace(/^Value error,\s*/i, "")));
            } else if (data.errors && Array.isArray(data.errors)) {
                data.errors.forEach((errMsg: string) => toast.error(errMsg));
            } else {
                toast.error(data.message || data.detail || "Processing failed");
            }
        } finally {
            setLoading(false);
        }
    };

    return {
        xmlData,
        setXmlData,
        departments,
        setDepartments,
        priorityOrder,
        setPriorityOrder,
        results,
        setResults,
        loading,
        parsingStats,
        setParsingStats,
        handleXmlUpload,
        clearXmlData,
        removeDepartment,
        addToPriority,
        removePriority,
        movePriorityUp,
        movePriorityDown,
        handleSubmit
    };
}

import { ProcessResponse, HistoryEntry, HistoryDetail } from "../types/logistics";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://192.168.1.4:8000";

export const api = {
    async processLogistics(payload: any): Promise<ProcessResponse> {
        const response = await fetch(`${API_BASE_URL}/api/v1/process-logistics`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const data = await response.json();
        if (!response.ok) {
            throw data; // Throw the error body for the hook to handle
        }
        return data;
    },

    async getHistory(): Promise<{ history: HistoryEntry[] }> {
        const response = await fetch(`${API_BASE_URL}/api/v1/history`);
        if (!response.ok) throw new Error("Failed to fetch history");
        return response.json();
    },

    async getHistoryEntry(id: string): Promise<HistoryDetail> {
        const response = await fetch(`${API_BASE_URL}/api/v1/history/${id}`);
        if (!response.ok) throw new Error("Failed to load history entry");
        return response.json();
    },

    async deleteHistoryEntry(id: string): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/api/v1/history/${id}`, {
            method: "DELETE",
        });
        if (!response.ok) throw new Error("Failed to delete history entry");
    }
};

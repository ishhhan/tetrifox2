import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { History, X } from "lucide-react";
import { HistoryEntry } from "../../types/logistics";

interface HistoryDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    loading: boolean;
    historyList: HistoryEntry[];
    onLoad: (id: string) => void;
    onDelete: (id: string) => void;
    onView: () => void;
}

export function HistoryDialog({
    open,
    onOpenChange,
    loading,
    historyList,
    onLoad,
    onDelete,
    onView
}: HistoryDialogProps) {

    const formatTimestamp = (timestamp: string) => {
        return new Date(timestamp).toLocaleString();
    };

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogTrigger asChild>
                <Button
                    variant="outline"
                    className="border-border hover:bg-accent"
                    onClick={onView}
                >
                    <History className="w-4 h-4 mr-2" />
                    View History
                </Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg">
                <DialogHeader>
                    <DialogTitle>Run History</DialogTitle>
                </DialogHeader>
                <div className="max-h-80 overflow-y-auto">
                    {loading ? (
                        <p className="text-center py-4 text-muted-foreground">Loading...</p>
                    ) : historyList.length === 0 ? (
                        <p className="text-center py-4 text-muted-foreground">No history yet. Run a process first.</p>
                    ) : (
                        <div className="space-y-2">
                            {historyList.map((entry) => (
                                <div
                                    key={entry.id}
                                    className="flex items-center justify-between p-3 bg-secondary hover:bg-secondary/80 rounded-lg transition-colors"
                                >
                                    <div>
                                        <p className="font-medium text-sm">{formatTimestamp(entry.timestamp)}</p>
                                        <p className="text-xs text-muted-foreground">{entry.total_processed} parcels</p>
                                    </div>
                                    <div className="flex gap-2">
                                        <button
                                            onClick={() => onLoad(entry.id)}
                                            className="px-3 py-1 bg-primary text-primary-foreground rounded text-xs font-medium hover:bg-primary/90 transition-colors"
                                        >
                                            Load
                                        </button>
                                        <button
                                            onClick={() => onDelete(entry.id)}
                                            className="text-muted-foreground hover:text-destructive transition-colors p-1"
                                            title="Delete"
                                        >
                                            <X className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}

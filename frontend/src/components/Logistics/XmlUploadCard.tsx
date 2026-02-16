import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, Trash2 } from "lucide-react";

interface XmlUploadCardProps {
    xmlData: string;
    onUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onClear: () => void;
}

export function XmlUploadCard({ xmlData, onUpload, onClear }: XmlUploadCardProps) {
    return (
        <Card className="mb-8 border-2 hover:shadow-lg transition-all duration-200">
            <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                    <label className="text-base font-semibold">Upload XML</label>
                    {xmlData && (
                        <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950"
                            onClick={onClear}
                        >
                            <Trash2 className="w-4 h-4 mr-2" /> Clear XML
                        </Button>
                    )}
                </div>
                <div className="relative border-2 border-dashed border-slate-300 rounded-lg p-8 text-center cursor-pointer hover:border-slate-400 transition">
                    <input
                        type="file"
                        accept=".xml"
                        onChange={onUpload}
                        className="absolute inset-0 opacity-0 cursor-pointer"
                    />
                    <Upload className="w-6 h-6 mx-auto mb-2 text-slate-400" />
                    <p className="text-slate-600">
                        {xmlData ? "✓ XML loaded" : "Click or drag to upload XML file"}
                    </p>
                </div>
            </div>
        </Card>
    );
}

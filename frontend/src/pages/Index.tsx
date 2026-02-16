import React from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { toast } from "sonner";
import { useTheme } from "next-themes";
import { Sun, Moon, Trash2 } from "lucide-react";

// Custom Components
import { WeightDepartment } from "@/components/DepartmentForms/WeightDepartment";
import { ValueDepartment } from "@/components/DepartmentForms/ValueDepartment";
import { PostalDepartment } from "@/components/DepartmentForms/PostalDepartment";
import { CityDepartment } from "@/components/DepartmentForms/CityDepartment";
import { ClientDepartment } from "@/components/DepartmentForms/ClientDepartment";
import { ResultsTable } from "@/components/Logistics/ResultsTable";
import { HistoryDialog } from "@/components/Logistics/HistoryDialog";
import { ParsingStatsCard } from "@/components/Logistics/ParsingStatsCard";
import { PriorityOrderCard } from "@/components/Logistics/PriorityOrderCard";
import { ActiveDepartmentsCard } from "@/components/Logistics/ActiveDepartmentsCard";
import { XmlUploadCard } from "@/components/Logistics/XmlUploadCard";

// Hooks
import { useLogistics } from "@/hooks/useLogistics";
import { useHistory } from "@/hooks/useHistory";
import { useDepartmentValidation } from "@/hooks/useDepartmentValidation";
import { DepartmentRule } from "@/types/logistics";

export default function Index() {
  const { theme, setTheme } = useTheme();

  // 1. Core Logistics Logic
  const {
    xmlData,
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
  } = useLogistics();

  // 2. Validation Hook
  const { validateNewDepartment } = useDepartmentValidation(departments);

  // 3. History Hook
  const history = useHistory({
    setResults,
    setDepartments,
    setPriorityOrder,
    setParsingStats
  });

  // Generic Department Handler
  const handleAddDept = (newDept: DepartmentRule) => {
    const error = validateNewDepartment(newDept);
    if (error) return toast.error(error);
    setDepartments([...departments, newDept]);
    toast.success(`Department "${newDept.name}" added`);
  };

  return (
    <div className="min-h-screen bg-background text-foreground p-6 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 flex justify-between items-start">
          <div>
            <h1 className="text-4xl font-bold">Tetrifox</h1>
            <p className="text-muted-foreground mt-2">Logistics Processing Engine</p>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="border-border hover:bg-accent"
            >
              {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </Button>

            <HistoryDialog
              open={history.historyOpen}
              onOpenChange={history.setHistoryOpen}
              loading={history.loading}
              historyList={history.historyList}
              onLoad={history.loadEntry}
              onDelete={history.deleteEntry}
              onView={history.fetchHistory}
            />
          </div>
        </div>

        {/* Configuration Section */}
        <XmlUploadCard
          xmlData={xmlData}
          onUpload={handleXmlUpload}
          onClear={clearXmlData}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <PriorityOrderCard
            priorityOrder={priorityOrder}
            onAdd={addToPriority}
            onRemove={removePriority}
            onMoveUp={movePriorityUp}
            onMoveDown={movePriorityDown}
          />

          <ActiveDepartmentsCard
            departments={departments}
            onRemove={removeDepartment}
            onClearAll={() => {
              setDepartments([]);
              toast.success("All departments cleared");
            }}
          />
        </div>

        {/* Forms Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card className="p-6 border-2">
            <h3 className="font-bold mb-4">Weight Based</h3>
            <WeightDepartment onAdd={(d) => handleAddDept({ ...d, field: "weight", type: "range" })} />
          </Card>
          <Card className="p-6 border-2">
            <h3 className="font-bold mb-4">Value Based</h3>
            <ValueDepartment onAdd={(d) => handleAddDept({ ...d, field: "value", type: "range" })} />
          </Card>
          <Card className="p-6 border-2">
            <h3 className="font-bold mb-4">Postal Based</h3>
            <PostalDepartment onAdd={(d) => handleAddDept({ ...d, field: "postal_code", type: "match" })} />
          </Card>
          <Card className="p-6 border-2">
            <h3 className="font-bold mb-4">City Based</h3>
            <CityDepartment onAdd={(d) => handleAddDept({ ...d, field: "city", type: "match" })} />
          </Card>
          <Card className="p-6 border-2">
            <h3 className="font-bold mb-4">Client Based</h3>
            <ClientDepartment onAdd={(d) => handleAddDept({ ...d, field: "recipient", type: "match" })} />
          </Card>
        </div>

        {/* Actions */}
        <div className="mb-8 flex justify-center gap-4">
          <Button
            size="lg"
            variant="ghost"
            className="px-8 text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950"
            onClick={() => {
              clearXmlData();
              setDepartments([]);
              setPriorityOrder([]);
              toast.success("All configurations cleared");
            }}
            disabled={loading}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Clear All
          </Button>

          <Button
            size="lg"
            className="px-12 bg-slate-900 hover:bg-slate-800 text-white"
            onClick={handleSubmit}
            disabled={loading}
          >
            {loading ? "Processing..." : "Submit"}
          </Button>
        </div>

        {/* Results */}
        {parsingStats && <div className="mb-8"><ParsingStatsCard stats={parsingStats} /></div>}
        {results.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold">Processed Parcels</h2>
            <ResultsTable data={results} />
          </div>
        )}
      </div>
    </div>
  );
}

import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

interface ValueDepartmentProps {
  onAdd: (data: { name: string; min?: number; max?: number }) => void;
}

// Max absolute limit
const MAX_LIMIT = 100000;

export function ValueDepartment({ onAdd }: ValueDepartmentProps) {
  const [min, setMin] = useState<string>("");
  const [max, setMax] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const handleMinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = parseFloat(e.target.value);
    if (!isNaN(value) && value < 0) {
      setMin("0");
    } else {
      setMin(e.target.value);
    }
    setError(null);
  };

  const handleMaxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = parseFloat(e.target.value);
    if (!isNaN(value) && value < 0) {
      setMax("0");
    } else if (!isNaN(value) && value > MAX_LIMIT) {
      setMax(MAX_LIMIT.toString());
    } else {
      setMax(e.target.value);
    }
    setError(null);
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const name = formData.get("name") as string;
    const minVal = min ? parseFloat(Number(min).toFixed(2)) : undefined;
    const maxVal = max ? parseFloat(Number(max).toFixed(2)) : undefined;

    let finalMax = maxVal;
    let finalMin = minVal;

    // Auto-calculate max if only min is provided (Max = Min * 10)
    if (minVal !== undefined && finalMax === undefined) {
      finalMax = minVal * 10;
    }
    // Auto-calculate min if only max is provided (Min = Max / 10)
    else if (maxVal !== undefined && finalMin === undefined) {
      finalMin = Math.max(0, maxVal / 10);
    }

    if (finalMin !== undefined && finalMax !== undefined) {
      if (finalMin > 0 && finalMax > finalMin * 10) {
        setError("Range too wide: Max cannot exceed 10x Min");
        return;
      }
      if (finalMin > finalMax) {
        setError("Min cannot be greater than Max");
        return;
      }
    }

    if (!name) return;
    onAdd({ name, min: finalMin, max: finalMax });

    // Reset form
    e.currentTarget.reset();
    setMin("");
    setMax("");
    setError(null);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label className="text-sm">Department</Label>
        <Input name="name" placeholder="Enter name" className="mt-1" required />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <Label className="text-sm">Min (€)</Label>
          <Input
            name="min"
            type="number"
            step="0.01"
            placeholder="Min"
            className="mt-1"
            value={min}
            onChange={handleMinChange}
            min={0}
          />
        </div>
        <div>
          <Label className="text-sm">Max (€)</Label>
          <Input
            name="max"
            type="number"
            step="0.01"
            placeholder={`Max (≤${MAX_LIMIT})`}
            className="mt-1"
            value={max}
            onChange={handleMaxChange}
            min={0}
            max={MAX_LIMIT}
          />
        </div>
      </div>
      {error && <p className="text-xs text-red-500 font-medium">{error}</p>}
      <Button type="submit" variant="outline" size="sm" className="w-full text-slate-600">
        <Plus className="w-4 h-4 mr-2" />
        Add Department
      </Button>
    </form>
  );
}

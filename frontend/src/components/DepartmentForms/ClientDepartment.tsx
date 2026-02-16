import React from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

interface ClientDepartmentProps {
  onAdd: (data: { name: string; match_value: string }) => void;
}

export function ClientDepartment({ onAdd }: ClientDepartmentProps) {
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const name = formData.get("name") as string;
    const match_value = formData.get("recipient") as string;

    if (!name || !match_value) return;
    onAdd({ name, match_value });
    e.currentTarget.reset();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label className="text-sm">Category</Label>
        <Input name="name" placeholder="Enter category" className="mt-1" required />
      </div>
      <div>
        <Label className="text-sm">Name</Label>
        <Input name="recipient" placeholder="Enter name" className="mt-1" required />
      </div>
      <Button type="submit" variant="outline" size="sm" className="w-full text-slate-600">
        <Plus className="w-4 h-4 mr-2" />
        Add Department
      </Button>
    </form>
  );
}

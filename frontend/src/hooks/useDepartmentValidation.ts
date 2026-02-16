import { DepartmentRule, DepartmentType } from "../types/logistics";
import { toast } from "sonner";

export function useDepartmentValidation(departments: DepartmentRule[]) {
    const validateNewDepartment = (newDept: DepartmentRule): string | null => {
        // 1. Check Name Duplication
        if (departments.some((d) => d.name.toLowerCase() === newDept.name.toLowerCase())) {
            return `Department name "${newDept.name}" already exists`;
        }

        // 2. Check Range Overlap
        // Logic: (min, max] ranges don't overlap if max(min1, min2) >= min(max1, max2)
        if (newDept.type === "range" && newDept.min !== undefined && newDept.max !== undefined) {
            const hasOverlap = departments.some((d) => {
                if (d.field !== newDept.field || d.type !== "range") return false;
                const dMin = d.min ?? -Infinity;
                const dMax = d.max ?? Infinity;
                const nMin = newDept.min ?? -Infinity;
                const nMax = newDept.max ?? Infinity;
                // Strict inequality for (min, max] ranges
                return Math.max(dMin, nMin) < Math.min(dMax, nMax);
            });
            if (hasOverlap) return `Range overlaps with an existing ${newDept.field} department`;
        }

        // 3. Check Match Duplication
        if (newDept.type === "match") {
            if (departments.some(d => d.field === newDept.field && d.match_value?.toLowerCase() === newDept.match_value?.toLowerCase())) {
                return `Duplicate Match rule for ${newDept.field}`;
            }
        }

        return null;
    };

    return { validateNewDepartment };
}

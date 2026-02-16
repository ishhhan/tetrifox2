# ⚛️ Frontend Architecture & Component Logic

**Purpose**: A responsive, interactive dashboard that manages the user's workflow, validates input in real-time, and visualizes complex routing data.

## 🏗 Code Structure

The frontend is built on **React** with a separation between **UI (Components)** and **Logic (Hooks)**.

```
frontend/src/
├── hooks/           # [Brain] Pure Business Logic
│   ├── useLogistics.ts            # Manages the main "Submit" lifecycle
│   ├── useDepartmentValidation.ts # Prevents duplicate/invalid rules
│   └── useHistory.ts              # Syncs past runs with the backend
│
├── components/      # [View] Smart UI Elements
│   ├── Logistics/
│   │   ├── ActiveDepartmentsCard.tsx # Displays active rules + badges
│   │   ├── ResultsTable.tsx          # Sortable data grid with formatting
│   │   └── XmlUploadCard.tsx         # Drag-and-drop zone
│   │
│   └── DepartmentForms/             # Logic-heavy forms
│       ├── WeightDepartment.tsx     # Auto-calculates ranges (Min+10)
│       └── ValueDepartment.tsx      # Auto-calculates ranges (Min*10)
│
└── lib/             # [Network]
    └── api.ts       # Typed API client for backend communication
```

## 🧠 Key Logic Flows

### 1. Smart Constraint Forms (`WeightDepartment.tsx`)
We don't just take user input; we guide it.
*   **Auto-Fill Logic**:
    *   If User enters `Min: 10`, the code automatically sets `Max: 20` (Min + 10).
    *   If User enters `Max: 50`, the code sets `Min: 40` (Max - 10).
*   **Why?**: This guarantees that "Infinite" ranges are impossible, preventing backend validation errors.

### 2. The Logic Hook (`useLogistics.ts`)
This hook is the central controller for the main page `Index.tsx`.
*   It holds the state for `xmlData`, `departments`, and `results`.
*   It exposes a simple `handleSubmit()` function.
*   When called, it bundles all state into a standardized JSON payload and calls `api.processLogistics()`.

### 3. Real-Time Validation (`useDepartmentValidation.ts`)
Before you can even click "Add Department":
*   It scans all existing departments.
*   It checks for **Name Duplicates** (e.g., two "Berlin Express").
*   It checks for **Range Overlaps** (e.g., 0-10 and 5-15).
*   If an error is found, it blocks the action immediately.

### 4. Results Formatting (`ResultsTable.tsx`)
It transforms raw data for readability:
*   Numbers are "Commified" (e.g., `1000` -> `1,000`).
*   Routes are visually chained with arrows (`Weight Rule → City Rule`).

# 🐍 Backend Architecture & Logic

**Purpose**: The core decision engine that ingests XML, applies user-defined rules, and calculates optimal routes.

## 🏗 System Structure

The backend follows a **Modular Layered Architecture** to separate concerns:

```
backend/
├── api/             # [Interface Layer]
│   ├── logistics.py # Handles the main POST /process-logistics request
│   └── history.py   # Handles CRUD operations for past runs
│
├── services/        # [Business Logic Layer]
│   ├── logistics/   # The Brain
│   │   ├── compute.py # (Orchestrator) Coordinates Parsing -> Validation -> Routing
│   │   ├── parser.py  # (XML Parser) Resilient XML reading (handles typos)
│   │   └── engine.py  # (Routing Engine) Matches priorities to rules
│   └── history/     # Data Persistence
│       └── store.py # In-memory storage for session history
│
├── validators/      # [Safety Layer]
│   └── logic.py     # Centralized rules (e.g., "Weight Max must be > Min")
│
└── dtos/            # [Data Contract Layer]
    ├── request.py   # Strict patterns for incoming JSON
    └── response.py  # Standardized output formats
```

## 🧠 Core Functions

### 1. The Logistics Orchestrator (`compute.py`)
This is the "Manager" of the system. When a request comes in:
1.  **Collecting Phase**: It calls `BusinessValidator` to check all inputs for errors (overlaps, invalid ranges).
2.  **Parsing Phase**: It sends raw XML to `parser.py` to extract `Parcel` objects.
3.  **Execution Phase**: It initializes the `RoutingEngine` with the user's priority order.
4.  **History Phase**: It saves the final result to `HistoryStore` for later retrieval.

### 2. The XML Parser (`parser.py`)
Designed to be **Resilient**. It doesn't just read perfect XML; it handles real-world messiness:
*   **Typo Correction**: Finds `<Receipient>` or `<recipient>` even if misspelled.
*   **Deep Search**: Locates address fields regardless of nesting depth.

### 3. The Routing Engine (`engine.py`)
Decides the fate of a parcel based on **Priority Order**:
*   If you set `["Weight", "City"]` as priority:
    *   It *first* checks if the parcel matches a Weight Department.
    *   If yes -> Assigned. Stop.
    *   If no -> It checks the City Department.
    *   If no -> Parcel is marked "Unassigned".

### 4. Consolidated Validation (`logic.py`)
A single source of truth for all business rules, defined with constants for easy maintenance:

#### Constants
| Constant | Value | Description |
|----------|-------|-------------|
| `MAX_WEIGHT` | 1000 | Maximum allowed weight in kg |
| `MAX_WEIGHT_SPAN` | 10 | Maximum range span for weight departments |
| `MAX_VALUE` | 100000 | Maximum allowed parcel value in € |
| `MAX_VALUE_RATIO` | 10 | Max value cannot exceed 10x the min value |

#### Range Semantics: `(min, max]`
All range-based rules use **exclusive min, inclusive max** logic:
- A parcel with weight `10` does **NOT** match a rule `(10, 20]`
- A parcel with weight `20` **DOES** match a rule `(10, 20]`

#### Overlap Detection
Adjacent ranges like `(0, 10]` and `(10, 20]` are allowed because they don't share any values:
- `(0, 10]` covers `0 < weight <= 10`
- `(10, 20]` covers `10 < weight <= 20`
- Value `10` belongs to the first range only.

#### Auto-Default for Value Fields
When creating a `value` department with only `min` specified, `max` is auto-calculated as `min * 10` (capped at 100,000).

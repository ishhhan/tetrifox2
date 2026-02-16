# 🎯 Tetrifox Backend — 45 Minute Interview Walkthrough

---

## ⏱️ TIME BREAKDOWN

| Section | Duration | What to Cover |
|:--------|:--------:|:--------------|
| 1. Project Overview & Architecture | 5 min | Big picture, folder structure, tech stack |
| 2. Entry Point & API Layer | 5 min | `main.py`, `api/logistics.py`, Dependency Injection |
| 3. Data Flow (Request → Response) | 8 min | Full journey of a request through the system |
| 4. Validation Layer (★ Star Section) | 10 min | DTO validation, Business rules, Error collection |
| 5. XML Parser & Deduplication | 7 min | Parsing, missing fields, duplicate detection |
| 6. Routing Engine | 5 min | Priority sorting, rule matching |
| 7. Design Patterns & SOLID | 3 min | Patterns used and why |
| 8. Q&A Buffer | 2 min | Anticipate questions |

---

## 📌 SECTION 1: Project Overview & Architecture (5 min)

### What to Say:
> "Tetrifox is a logistics routing system. Users upload XML data containing parcels 
> (packages with weight, value, address), define department rules (like 'Express handles 
> 0-5kg'), set priority order, and the system assigns each parcel to the correct department."

### Folder Structure (Show this):
```
backend/
├── main.py                    # App entry point (FastAPI + Uvicorn)
├── api/                       # API Routes (thin controllers)
│   ├── logistics.py           # POST /process-logistics
│   └── history.py             # GET/DELETE /history
├── core/                      # Cross-cutting concerns
│   ├── config.py              # Logger setup
│   └── exceptions.py          # Custom exceptions + handlers
├── dtos/                      # Data Transfer Objects (Pydantic)
│   ├── request.py             # Input validation (DepartmentRuleDTO, LogisticsRequest)
│   └── response.py            # Output formatting (ParcelOutputDTO, etc.)
├── schemas/                   # Internal domain models (dataclasses)
│   ├── domain.py              # Parcel, InternalRule
│   └── parsing.py             # ParsingStats, RemovedParcel
├── validators/                # Business validation logic
│   └── logic.py               # ErrorCollector + BusinessValidator
├── services/                  # Business logic layer
│   ├── dependencies.py        # Dependency Injection container
│   ├── logistics/
│   │   ├── compute.py         # LogisticsOrchestrator (Facade)
│   │   ├── engine.py          # RoutingEngineService
│   │   ├── parser.py          # XmlParserService
│   │   └── rules.py           # RuleEvaluator
│   └── history/
│       └── store.py           # HistoryStore (in-memory)
└── tests/                     # Unit tests
    ├── test_engine.py
    ├── test_orchestrator.py
    ├── test_parser.py
    └── test_ranges.py
```

### Key Points to Mention:
- **Tech Stack**: Python, FastAPI, Pydantic v2, Uvicorn
- **Architecture**: Layered (API → Service → Domain)
- **Separation of Concerns**: DTOs ≠ Domain Models ≠ Response Models

---

## 📌 SECTION 2: Entry Point & API Layer (5 min)

### Files to Open: `main.py` → `api/logistics.py` → `services/dependencies.py`

### What to Say:

#### `main.py` (30 sec):
> "This is the entry point. It creates the FastAPI app, registers CORS middleware,
> exception handlers, and includes routers with versioned prefixes like `/api/v1/`."

#### `api/logistics.py` (2 min):
> "This is intentionally thin — just 18 lines. It receives the request, 
> delegates to the orchestrator, and returns the response. 
> Notice the `Depends(get_orchestrator)` — this is FastAPI's Dependency Injection."

**Key Line to Highlight:**
```python
orchestrator: LogisticsOrchestrator = Depends(get_orchestrator)
```
> "Instead of manually creating the orchestrator with all its dependencies,
> FastAPI calls `get_orchestrator()` which assembles it with the parser and history store.
> This follows the Dependency Inversion Principle from SOLID."

#### `services/dependencies.py` (1.5 min):
> "This is our DI container. It's a factory that wires everything together.
> The orchestrator doesn't know or care WHERE its parser comes from — 
> it just receives one. This makes testing easy: I can swap in a mock parser."

---

## 📌 SECTION 3: Data Flow — Request to Response (8 min)

### File to Open: `dtos/request.py` → `compute.py`

### Draw this flow (or explain verbally):
```
[User Request (JSON)]
        ↓
[1. Pydantic DTO Validation]     ← request.py (auto-defaults, range checks, overlap checks)
        ↓
[2. Orchestrator]                ← compute.py (collects errors, coordinates everything)
        ↓
  ┌─────┴─────┐
  ↓           ↓
[3. XML      [4. Map DTOs to
 Parser]      Domain Rules]
  ↓               ↓
[5. Routing Engine]              ← engine.py + rules.py
        ↓
[6. Map Domain → Output DTOs]   ← response.py
        ↓
[7. Save to History]            ← store.py (Fail-Open: errors logged, not thrown)
        ↓
[8. Return JSON Response]
```

### What to Say:
> "The request goes through 8 stages. First, Pydantic validates the input — 
> it auto-calculates missing max values, checks ranges, and detects duplicate departments.
> Then the Orchestrator takes over. It's a Facade that coordinates parsing, validation, 
> routing, and history saving. If anything fails, errors are collected (not thrown immediately)
> and returned as a batch."

### Key Design Decision to Highlight:
> "I made a deliberate choice to have TWO types of validators:
> - **Throwing validators** (in DTOs) — fail fast on first error  
> - **Collecting validators** (in Orchestrator) — gather ALL errors before responding
> 
> This gives users a complete picture of what's wrong, not just the first issue."

---

## 📌 SECTION 4: Validation Layer ★ STAR SECTION (10 min)

### Files to Open: `validators/logic.py` → `dtos/request.py`

### 4A. ErrorCollector Pattern (2 min)
> "Instead of throwing exceptions one by one, I built an ErrorCollector class 
> that accumulates errors. When we're done validating, we check `has_errors()` 
> and raise them all at once as an `AggregatedValidationError`."

**Highlight the class:**
```python
class ErrorCollector:
    def add(self, error: str) -> None
    def has_errors(self) -> bool
    @property
    def errors(self) -> List[str]  # Returns .copy() for safety
```

### 4B. BusinessValidator Constants (1 min)
> "All business limits are centralized as class constants:
> - MAX_WEIGHT = 1000 kg
> - MAX_WEIGHT_SPAN = 10 kg (range width limit)
> - MAX_VALUE = 100,000 €  
> - MAX_VALUE_RATIO = 10x (max can't exceed 10× min)
> 
> Changing one number here updates the entire system."

### 4C. Range Validation — `_check_range_rules` (3 min)
> "This is the single source of truth for range validation. It checks:
> 1. No negative minimums
> 2. Min ≤ Max
> 3. Field-specific rules (weight span ≤ 10kg, value ratio ≤ 10x)
> 
> Both throwing and collecting validators call this same method — DRY principle."

### 4D. Overlap Detection — `validate_department_overlap` (4 min)
> "This is the most complex validation. It does two things:"

**Phase 1 — Name Uniqueness:**
> "Case-insensitive check using a Set. O(n) time complexity."

**Phase 2 — Range Overlap:**
> "Groups rules by field using `setdefault()`, then compares every pair.
> For None values (open-ended ranges), I normalize to ±infinity.
> The overlap formula is: `max(min1, min2) < min(max1, max2)`"

**Give an example:**
> "If Express is 0-5kg and Standard is 3-8kg, then max(0,3)=3 < min(5,8)=5, 
> so they overlap. The system rejects this."

### 4E. Auto-Defaults in DTO (1 min)
> "In `request.py`, I use Pydantic's `model_validator(mode='before')` to 
> auto-calculate missing max values BEFORE validation runs.
> For value fields: max = min × 10. For weight: max = min + 10.
> This runs on raw dict data before the object is even created."

---

## 📌 SECTION 5: XML Parser & Deduplication (7 min)

### File to Open: `services/logistics/parser.py`

### What to Say:
> "The parser handles messy real-world XML. It has 4 safety layers:"

### Layer 1 — Flexible Tag Names (1 min):
> "XML might have `<Receipient>` or `<Recipient>` (common typo). 
> The parser tries multiple spellings before giving up."

### Layer 2 — Missing Field Detection (2 min):
> "The `get_text()` helper safely extracts text from XML nodes. 
> If a field is missing or empty, the parcel is discarded and tracked in stats.
> We use a `missing_in_this_parcel` list, and if it's not empty, we `continue` 
> to the next parcel — skipping all downstream logic."

### Layer 3 — Numeric Validation (1 min):
> "Weight and Value must be valid numbers. `float('ABC')` would crash, 
> so we wrap it in try/except. Negative values are auto-corrected to 0."

### Layer 4 — Dual Deduplication (2 min):
> "Two types of duplicate detection:
> 1. **ID-based**: Same parcel ID appears twice → skip
> 2. **Content-based**: Different IDs but identical data → skip
> 
> The content hash is a string fingerprint: `recipient|city|street|postal|weight|value`.
> Both use `continue` to skip the duplicate without processing it further."

### Stats Tracking (1 min):
> "Every skip, discard, and missing field is tracked in a `ParsingStats` object.
> This gets returned to the frontend so users see exactly what happened to their data."

---

## 📌 SECTION 6: Routing Engine (5 min)

### Files to Open: `engine.py` → `rules.py`

### Engine Initialization (2 min):
> "The engine validates its inputs in `__init__` — defense in depth. 
> Even if DTO validation was bypassed, the engine catches invalid fields or types."

### Priority Sorting (1.5 min):
> "Departments are sorted by user-defined priority using `enumerate` to build 
> a priority map. Fields not in the priority list get the lowest priority.
> Python's stable sort preserves original order for equal priorities."

### Rule Matching — `rules.py` (1.5 min):
> "Two matching strategies:
> - **Range**: Checks if `min < parcel_value <= max` (open-ended via ±infinity)
> - **Match**: Case-insensitive string comparison
> 
> Each parcel can match multiple departments — they all get assigned."

---

## 📌 SECTION 7: Design Patterns & SOLID Principles (3 min)

### Patterns Used:
| Pattern | Where | Why |
|:--------|:------|:----|
| **Facade** | `LogisticsOrchestrator` | Single entry point for complex workflow |
| **Dependency Injection** | `Depends()` + `dependencies.py` | Loose coupling, testability |
| **Collector Pattern** | `ErrorCollector` | Batch error reporting |
| **Strategy Pattern** | `RuleEvaluator.matches()` | Different matching logic (range vs match) |
| **Factory Pattern** | `get_orchestrator()` | Creates configured objects |
| **Fail-Open** | History save in `compute.py` | Auxiliary failures don't block user response |

### SOLID Principles:
- **S**ingle Responsibility: Each file/class has one job
- **O**pen/Closed: New rule types can be added without modifying existing code
- **D**ependency Inversion: Orchestrator depends on abstractions (injected services)

---

## 📌 SECTION 8: Anticipated Interview Questions

### Q1: "Why not use a database?"
> "Currently using in-memory storage (HistoryStore) for simplicity. 
> The architecture supports swapping to a DB — just create a new store class 
> and register it in `dependencies.py`. No other code changes needed."

### Q2: "How do you handle invalid XML?"
> "Three layers: 
> 1. Pydantic validator checks XML structure upfront
> 2. Parser catches `ET.ParseError` and raises custom `XmlParsingError`
> 3. FastAPI exception handler converts it to a clean 422 JSON response"

### Q3: "What happens if both min and max are None?"
> "The system treats it as a 'catch-all' rule (-infinity to +infinity). 
> Every parcel matches. The overlap check prevents creating conflicting rules 
> for the same field."

### Q4: "Why two types of validators (throwing vs collecting)?"
> "Throwing validators in DTOs give immediate feedback during data entry.
> Collecting validators in the orchestrator gather ALL issues across 
> departments, priorities, and XML — giving users a complete error report."

### Q5: "How do you prevent duplicate departments?"
> "Two checks: Case-insensitive name uniqueness using a Set, and 
> range overlap detection using the formula max(min1,min2) < min(max1,max2) 
> with infinity normalization for open-ended ranges."

### Q6: "What is the time complexity of overlap detection?"
> "O(n²) per field group — comparing every pair. For typical use cases 
> (5-10 departments), this is negligible. For scale, we could use 
> interval trees (O(n log n))."

---

## 🎤 PRO TIPS FOR THE INTERVIEW

1. **Start with a DEMO**: Run the app, show Swagger UI (`/docs`), process a sample request. Visual impact > code walkthrough.
2. **Show the Error Handling**: Intentionally send bad data and show how the system responds with clean error messages.
3. **Navigate with Ctrl+-**: Jump into definitions and back quickly.
4. **Don't read code line by line**: Explain the WHY, not the WHAT. The interviewer can read code.
5. **Use the word "deliberately"**: "I deliberately chose X because Y" shows intentional design.
6. **Mention Trade-offs**: "I chose in-memory storage for speed, knowing I'd swap to DB later."

---

## 🗂️ FILE OPENING ORDER (For smooth navigation)

1. `main.py` (Entry point)
2. `api/logistics.py` (API route)
3. `services/dependencies.py` (DI container)
4. `dtos/request.py` (Input validation)
5. `validators/logic.py` (Business rules)
6. `services/logistics/compute.py` (Orchestrator)
7. `services/logistics/parser.py` (XML parsing)
8. `services/logistics/engine.py` + `rules.py` (Routing)
9. `core/exceptions.py` (Error handling)
10. `dtos/response.py` (Output formatting)

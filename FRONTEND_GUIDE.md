# 🦅 Tetrifox Frontend Guide for Reviewers

> **Use this guide to explain the code if your reviewer asks "Why is it structured like this?"**

## 1. Why so many small files? (Modularity)
**Question:** "Why didn't you just put everything in one file?"
**Answer:** "I followed the **Single Responsibility Principle**. Breaking the code into small pieces makes it:
1.  **Easier to Read**: You don't have to scroll through 1000 lines to find the 'Weight Input'.
2.  **Easier to Test**: We can test the 'Results Table' without loading the whole app.
3.  **Reusable**: I can use the same 'Department Card' in other places if needed."

## 2. Why use Custom Hooks? (`useLogistics`, `useHistory`)
**Question:** "What are these files in `hooks/`?"
**Answer:** "I separated the **Business Logic** (Calculations, API calls) from the **UI** (Buttons, Inputs).
-   **`useLogistics`**: Handles the math and state for the parcel routing.
-   **Component Files**: Only care about *showing* data, not calculating it.
This keeps the UI code clean and 'dumb'."

## 3. Why strict types? (TypeScript)
**Question:** "Why define all these interfaces in `types.ts`?"
**Answer:** "To prevent bugs before they happen. TypeScript ensures I can't accidentally send a 'String' to a function that expects a 'Number'. It acts like a safety net."

---

## 🔑 Key Features to Show Off

If they ask "What's cool about this app?", show them:

1.  **Smart Constraints**: "Try adding a Weight Department. If I type Min=10, it automatically sets Max=20. It prevents logic errors."
2.  **Real-time Validation**: "It won't let me add two departments with the same name."
3.  **Visual Feedback**: "The results table uses arrows (`->`) to show the route path clearly."
4.  **Auto-Formatting**: "Numbers automatically get commas (e.g., `1,000`) so they are easier to read."

## 📁 Cheat Sheet: Where is code located?

| Feature | File |
| :--- | :--- |
| **Main Page** | `src/pages/Index.tsx` |
| **Upload Logic** | `src/components/Logistics/XmlUploadCard.tsx` |
| **Math & State** | `src/hooks/useLogistics.ts` |
| **API Calls** | `src/lib/api.ts` |
| **Types** | `src/types/logistics.ts` |

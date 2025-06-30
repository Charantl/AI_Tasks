# Your Customized AI-Powered Debugging Workflow for React & TypeScript

This document outlines a complete, actionable debugging workflow tailored to your specific development environment. Its goal is to standardize your process, leverage the full power of AI in Cursor, and systematically reduce the time it takes to resolve issues.

---

## **Part 1: Debugging Automation & Asset Library**

This section covers the reusable assets and AI-driven steps you can take to automate and speed up debugging.

### **1.1. AI-Automated Analysis & Refactoring**

Your primary advantage is using an AI-native IDE. Let the AI do the heavy lifting.

*   **Code Explanation:** Before diving into a complex file, use Cursor's chat to ask: `Analyze the attached file @[filename] and explain its purpose, props, and state management logic.`
*   **Automated Fixes:** After identifying a bug, instead of just asking for an explanation, ask for the fix directly.
    *   **Example Prompt:** `The function 'addProduct' in @useCartProducts.ts directly mutates state. Refactor it to follow immutable patterns suitable for a React context.`
*   **AI-Generated Test Cases:** After fixing a bug, ensure it stays fixed by generating a test case.
    *   **Example Prompt:** `Based on the fix in @useCartProducts.ts, generate a new test case for Jest and React Testing Library that asserts the immutability of the 'addProduct' function. It should fail with the old code and pass with the new code.`

### **1.2. Your Reusable Debugging Templates**

Create a `/.debugging` folder in your project root to store these markdown templates. When a bug occurs, copy the relevant template, fill it out, and use it to track the issue.

#### **Template 1: Bug Triage Report (`bug-report-template.md`)**

```markdown
# Bug Report: [Brief, Descriptive Title]

- **Date:** `YYYY-MM-DD`
- **Status:** `New | In Progress | Resolved`
- **Severity:** `Critical | High | Medium | Low`
- **Related Issue/Ticket:** `[Link to GitHub Issue, Trello Card, etc.]`

---

### 1. Symptoms

(Describe what is happening. Include console errors, unexpected UI behavior, and screenshots if possible.)

### 2. Reproduction Steps

1.  Go to page `X`.
2.  Click button `Y`.
3.  Observe error `Z`.

### 3. AI Analysis Summary (Paste from Cursor)

(Paste the AI's explanation of the root cause here. This is your "first pass" analysis.)

### 4. Resolution & Verification

-   **Files Modified:** `[List of files]`
-   **Fix Applied:** (Briefly describe the fix, e.g., "Refactored to use immutable state updates.")
-   **Verification:** (How did you confirm the fix worked? E.g., "Manual test passed, new unit test `xyz.test.ts` created and passing.")
```

#### **Template 2: Performance Issue Report (`perf-report-template.md`)**

```markdown
# Performance Report: [Describe Bottleneck, e.g., "Excessive Re-renders in Filter Component"]

- **Date:** `YYYY-MM-DD`
- **Status:** `Investigating | Resolved`
- **Impact:** `High (blocks UI) | Medium (sluggish) | Low (minor)`

---

### 1. Observed Behavior

(Describe the performance issue. E.g., "The UI becomes sluggish when multiple filter checkboxes are clicked rapidly.")

### 2. AI Analysis & Profiling Summary

-   **React DevTools Profiler Screenshot:** `[Insert image of profiler graph showing re-renders]`
-   **AI Root Cause Analysis (Paste from Cursor):** (e.g., "The 'filterProducts' function was being recreated on every render, causing child components to re-render unnecessarily.")

### 3. Optimization & Verification

-   **Optimization Strategy:** (e.g., "Wrapped `filterProducts` in `useCallback` and memoized expensive calculations with `useMemo`.")
-   **Verification:**
    -   **Metric Before:** (e.g., "Component rendered in `150ms`.")
    -   **Metric After:** (e.g., "Component rendered in `8ms`.")
    -   **React DevTools Profiler Screenshot (After):** `[Insert image showing fewer re-renders]`
```

### **1.3. Your Custom Prompt Library**

Store these prompts somewhere accessible (e.g., in a markdown file in your `.debugging` folder). These are tailored to your common issues.

*   **For State Management Bugs:**
    > "Analyze the selected code from my React/TypeScript component. It's causing bugs related to state management. Identify any direct state mutations or violations of immutable patterns. Provide a refactored, secure version of the code using modern React hooks and principles."

*   **For Performance Bottlenecks:**
    > "The attached React component `@file` is experiencing performance issues. Analyze it for common React performance bottlenecks, specifically: excessive re-renders, lack of memoization (`useCallback`, `useMemo`), and inefficient data handling in loops or arrays. Suggest an optimized version of the code."

*   **For Security Vulnerabilities (XSS):**
    > "Scan the attached React file `@file` for potential client-side security vulnerabilities. Focus on unsafe HTML rendering (`dangerouslySetInnerHTML`), misuse of `href` attributes, and other potential XSS vectors. For each issue found, explain the risk and provide a secure code alternative."

*   **For Async/Error Handling:**
    > "Review the attached code, which handles an async API call. It lacks robust error handling. Refactor it to include a comprehensive `try/catch/finally` block. The solution should differentiate between network errors and HTTP status code errors, and it should update the React component's state (`isFetching`, `error`) correctly in all scenarios."

---

## **Part 2: Your Standardized Debugging Workflow (SOP)**

This is your step-by-step process, designed for consistency and efficiency.

### **Step 1: Identify & Document**
*   **Isolate the Bug:** As soon as you encounter a bug, stop and take a breath. Don't immediately start changing code.
*   **Create a Report:** Copy your `bug-report-template.md`, rename it (e.g., `2023-10-27-cart-update-bug.md`), and fill out the **Symptoms** and **Reproduction Steps**. This forces you to understand the problem before trying to solve it.

### **Step 2: Reproduce & Analyze with AI**
*   **Confirm Reproduction:** Follow your own steps to ensure the bug is reliably reproducible.
*   **Gather Context:** In Cursor, attach the relevant file(s) (e.g., `@useCartProducts.ts`).
*   **Run Your Prompt:** Select one of your custom prompts from the library that best fits the bug category. Run it in the chat.
*   **Document:** Paste the AI's analysis into the **AI Analysis Summary** section of your report.

### **Step 3: Fix & Generate Tests with AI**
*   **Apply the Fix:** Use Cursor to apply the AI's suggested code fix. Review the change to ensure you understand it.
*   **Generate Tests:** Immediately follow up with the AI: `Based on the fix you just provided for @[filename], generate a Jest/React Testing Library test case that would have caught this bug.`
*   **Add the Test:** Add the new test case to your test suite. Run it to confirm it passes with the fix.

### **Step 4: Verify Manually & Commit**
*   **Manual Check:** Manually run through your reproduction steps again. Confirm the bug is gone and no new bugs (regressions) have been introduced.
*   **Commit:** Commit your changes with a clear message.
    *   **Good Commit Message:** `fix(cart): Fix state mutation in addProduct`
    *   **Include Report Link:** In the commit body, you can add `Fixes #[GitHub Issue Number]` or simply reference your local report: `See debugging report: .debugging/2023-10-27-cart-update-bug.md`

### **Step 5: Review & Improve (The Post-Mortem)**
*   **Update Report:** Mark the bug report as `Resolved`.
*   **Knowledge Base:** This completed report is now an entry in your personal debugging knowledge base.
*   **Ask Why:** At the end of the week, review the reports you've created. Ask yourself: "Am I seeing a pattern?" If you've fixed three state mutation bugs, it might be time to read up on immutable patterns again or create a new, more specific prompt.

---

## **Part 3: Efficiency & Continuous Improvement**

### **How to Reduce Time-to-Resolution**
*   **Don't Skip Step 1:** The biggest time-waster in debugging is "poking around" without a clear hypothesis. The documentation step forces clarity.
*   **Trust the AI's First Pass:** Use the AI's analysis as your starting point. It's much faster than manually tracing logic through multiple files. Your job is to verify and guide the AI.

### **Building Your Personal Knowledge Base**
*   Your `.debugging` folder *is* your knowledge base.
*   Over time, it will contain a searchable history of every significant bug you've fixed, your thought process, and the solution. Before tackling a new bug, you can do a quick text search in this folder to see if you've ever solved something similar.

### **Tracking & Metrics**
As a solo developer, keep metrics simple and personal.
*   **Goal:** Reduce the number of "recurring" bugs.
*   **Track:** At the end of each week, categorize your bug reports.
    *   `State Management: 3`
    *   `Performance: 1`
    *   `Security: 0`
*   **Success Indicator:** If the count for a specific category starts trending down over the weeks, your workflow and learning are effective.

### **Iterating and Improving the Process**
*   **Refine Your Prompts:** If you find a prompt isn't giving you the exact output you want, tweak it. Add more context. Be more specific. Save the improved version.
*   **Refine Your Templates:** Is there a piece of information you wish you had captured in your bug reports? Add a new section to your template. Your workflow is a living document; treat it as such. 
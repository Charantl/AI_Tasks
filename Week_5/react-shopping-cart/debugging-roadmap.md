# 7-Day Debugging and Refactoring Roadmap: React Shopping Cart

This document provides a systematic 7-day plan for debugging and improving the React Shopping Cart application. Each day focuses on a specific category of issues, from critical security flaws to performance bottlenecks and user experience enhancements.

---

## Priority Assessment Overview

The codebase contains several issues of varying severity. Here is a summary of the key areas we will address:

1.  **Critical: Security & Data Integrity**
    *   **XSS Vulnerability**: The app was modified to render raw HTML using `dangerouslySetInnerHTML`, opening it to Cross-Site Scripting.
    *   **State Mutation Bug**: A function for adding products to the cart was directly mutating the state, leading to data corruption and unpredictable UI behavior.

2.  **High: Performance**
    *   **Inefficient Data Fetching**: The product filtering logic makes a new network request on every single filter change, causing significant performance degradation.
    *   **Lack of Memoization**: Key functions are recreated on every render, causing unnecessary re-renders of child components and impacting overall responsiveness.

3.  **Medium: Robustness & User Experience**
    *   **No API Error Handling**: The application does not gracefully handle failed network requests. If the product API is down, the app may crash or get stuck in a loading state.
    *   **Uncontrolled Components**: The filter checkboxes manage their own state, leading to complex and inefficient state synchronization in the parent component.
    *   **Minor UX Inconsistencies**: The cart behavior and alert messages could be more intuitive.

---

## The 7-Day Debugging Roadmap

### 📅 Day 1: Critical Security - Fixing XSS

**Goal**: Eliminate the Cross-Site Scripting (XSS) vulnerability.

-   **Analysis**: The component at `src/components/Products/Product/Product.tsx` was modified to use `dangerouslySetInnerHTML` to render the product title. This is the most severe type of vulnerability in a React app, as it allows arbitrary code execution if the `title` data is compromised.
-   **Debugging Strategy**:
    1.  **Locate**: Open `src/components/Products/Product/Product.tsx`.
    2.  **Identify**: Find the `<S.Title>` component that uses the `dangerouslySetInnerHTML` prop.
    3.  **Fix**: Replace the entire `dangerouslySetInnerHTML` attribute with standard React child rendering. React automatically sanitizes variables rendered this way, neutralizing the threat.
        -   **Vulnerable Code**: `<S.Title dangerouslySetInnerHTML={{ __html: title + "..." }} />`
        -   **Secure Code**: `<S.Title>{title}</S.Title>`
-   **Testing Strategy**:
    1.  **Manual**: After the fix, confirm that product titles render correctly and that no malicious code (like a JavaScript `alert()`) is executed.
    2.  **Unit Test**: Write a test for `Product.tsx` that provides a title with a script tag (e.g., `title="<script>alert(1)</script>"`). Assert that the rendered output does not contain a `<script>` tag in the DOM.
-   **Prevention**:
    *   **Policy**: Institute a strict team policy against using `dangerouslySetInnerHTML`.
    *   **Linting**: Implement a linter rule like `eslint-plugin-react/no-danger` that will fail the build if this prop is used.

---

### 📅 Day 2: Critical Bug - State & Data Integrity

**Goal**: Fix the state mutation bug that corrupts cart data.

-   **Analysis**: The `addProduct` function in `src/contexts/cart-context/useCartProducts.ts` was modified to directly mutate the `products` array from the context. This is a critical bug that breaks React's rendering model and leads to data corruption (e.g., prices being set to 0).
-   **Debugging Strategy**:
    1.  **Locate**: Open `src/contexts/cart-context/useCartProducts.ts`.
    2.  **Identify**: Analyze the `addProduct` function and note the use of `.push()` and `.forEach()` on the `products` state array, and the direct mutation of the `newProduct` argument.
    3.  **Fix**: Replace the function with an immutable version. Instead of modifying the existing array, create a *new* array using methods like `.map()` or the spread syntax (`[...]`).
-   **Testing Strategy**:
    1.  **Unit Test**: Create a test for the `useCartProducts` hook. In the test, call `addProduct` and assert two things:
        *   The new state returned by the hook is a *different array instance* than the previous state.
        *   The original `product` object you passed into the function has *not* been modified.
-   **Prevention**:
    *   **Immutability Helpers**: For complex state, introduce libraries like `Immer` to make immutable updates easier and less error-prone.
    *   **Education**: Ensure the team understands React's core principle of immutability.

---

### 📅 Day 3: High-Impact Performance - Network Inefficiency

**Goal**: Stop the application from re-fetching all products on every filter change.

-   **Analysis**: In `src/contexts/products-context/useProducts.tsx`, the `filterProducts` function calls `getProducts()` every time it runs. This is extremely inefficient.
-   **Debugging Strategy**:
    1.  **Locate**: Open `src/contexts/products-context/useProducts.tsx`.
    2.  **Identify**: Observe that `filterProducts` makes an API call.
    3.  **Fix**: Refactor the logic:
        *   Introduce a new state variable to the context, `allProducts`, to store the master list of products.
        *   Modify `fetchProducts` to populate `allProducts` (once) and the displayable `products` list.
        *   Rewrite `filterProducts` to filter the local `allProducts` array instead of making a network request.
-   **Testing Strategy**:
    1.  **Browser DevTools**: Open the "Network" tab in your browser. Verify that the request to `products.json` is made only *once* on page load, and not again when you click the filter checkboxes.
    2.  **Performance Timing**: Use `console.time('filtering')` and `console.timeEnd('filtering')` inside `filterProducts` to measure the execution time before and after the fix. You should see a dramatic improvement from `~50-100ms` (network-bound) to `<1ms` (memory-bound).
-   **Prevention**: Code reviews should specifically scrutinize functions that trigger data fetching to ensure they are not called excessively.

---

### 📅 Day 4: High-Impact Performance - Memoization

**Goal**: Prevent unnecessary re-renders by memoizing functions.

-   **Analysis**: Functions inside React components are recreated on every render. When these functions are passed as props to child components, they can trigger wasteful re-renders. Key functions like `fetchProducts` and `filterProducts` need to be memoized.
-   **Debugging Strategy**:
    1.  **Locate**: `src/contexts/products-context/useProducts.tsx`, `src/contexts/cart-context/useCartProducts.ts`, etc.
    2.  **Identify**: Look for functions that are passed as props or context values.
    3.  **Fix**: Wrap these functions in the `useCallback` hook. This ensures that the function instance only changes if its dependencies change.
-   **Testing Strategy**:
    1.  **React DevTools**: Use the React DevTools Profiler. Record a session where you interact with the app. After applying `useCallback`, profile again. The profiler will show you which components re-rendered, and you should see a reduction in "unnecessary" renders of child components that receive the memoized functions.
-   **Prevention**:
    *   **Linting**: The `eslint-plugin-react-hooks` package with the `exhaustive-deps` rule is essential for correctly managing the dependency arrays of `useCallback` and `useMemo`.

---

### 📅 Day 5: Robustness - API Error Handling

**Goal**: Make the application resilient to API failures.

-   **Analysis**: The `getProducts` service in `src/services/products.ts` had no error handling. A failed request would crash the promise chain.
-   **Debugging Strategy**:
    1.  **Locate**: `src/services/products.ts` and its consumer, `useProducts.tsx`.
    2.  **Fix**:
        *   In `getProducts`, wrap the `axios` call in a `try/catch` block. Check for specific `axios` error types to provide user-friendly error messages for network vs. HTTP errors.
        *   In `useProductsContext`, add a new state for `error`.
        *   In `fetchProducts` (`useProducts.tsx`), use a `try/catch/finally` block. The `catch` block should set the global error state. The `finally` block must set `isFetching` to `false` to prevent the UI from getting stuck.
-   **Testing Strategy**:
    1.  **Manual**: Temporarily change the API URL in `getProducts.ts` to an invalid endpoint. The UI should now display a user-friendly error message instead of crashing or showing an endless loader.
    2.  **Integration Test**: Use a library like Mock Service Worker (`msw`) to mock the API endpoint at the network level. Create a test case where the mock returns a 500 error, and assert that the React component correctly renders the error message from the context.
-   **Prevention**: Create a standardized API client or service template that includes robust error handling by default, so all new services follow a consistent, safe pattern.

---

### 📅 Day 6: User Experience (UX) and Component Logic

**Goal**: Refine the UI and simplify component logic.

-   **Analysis**: The filter checkboxes in `src/components/Filter/Filter.tsx` are "uncontrolled" and rely on a `Set` to manage their state, which is overly complex.
-   **Debugging Strategy**:
    1.  **Locate**: `src/commons/Checkbox/Checkbox.tsx` and `src/components/Filter/Filter.tsx`.
    2.  **Fix**: Refactor `Checkbox.tsx` to be a **controlled component**.
        *   It should accept an `isChecked` prop from its parent.
        *   Its `onChange` handler should simply call the `handleOnChange` prop without managing its own internal state.
        *   The `Filter` component will now be responsible for managing the `isChecked` state for each checkbox, which will simplify the `toggleCheckbox` logic immensely (no more `Set`).
-   **Testing Strategy**:
    1.  **Unit Test**: Update the tests for `Checkbox.tsx` to verify its behavior as a controlled component (i.e., its checked state changes when its `isChecked` prop changes).
    2.  **Manual**: Ensure the filtering functionality still works as expected after the refactor.
-   **Prevention**: When designing components, consciously decide whether they should be controlled or uncontrolled. For components that are part of a larger stateful system (like a form or filter group), controlled components are almost always the correct choice.

---

### 📅 Day 7: Final Polish & Code Hygiene

**Goal**: Clean up the codebase and prepare it for the future.

-   **Analysis**: The codebase has some "magic strings" and could benefit from better organization.
-   **Debugging Strategy**:
    1.  **Constants**: Move magic strings, like the array of available sizes in `Filter.tsx`, into a `constants.ts` file or derive them directly from the product data for better maintainability.
    2.  **Dead Code**: The `updateQuantitySafely` function in `useCartProducts.ts` is complex and its logic is already handled more cleanly inside `increaseProductQuantity` and `decreaseProductQuantity`. It can be removed.
    3.  **Review**: Read through the codebase one last time, looking for unclear variable names, missing comments on complex logic, or large components that could be broken down further.
-   **Testing Strategy**:
    *   **Regression Testing**: Perform a full manual test of the application's features (adding to cart, filtering, checking out) to ensure that the cleanup phase did not introduce any regressions.
-   **Prevention**:
    *   **Code Style**: Enforce a strict code style using tools like Prettier and ESLint.
    *   **CI/CD**: Integrate automated checks (linting, testing) into a Continuous Integration pipeline to catch issues before they are merged into the main branch. 
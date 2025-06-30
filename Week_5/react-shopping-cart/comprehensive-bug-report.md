# Comprehensive Bug Analysis Report: /src Directory

This document provides a comprehensive bug analysis of the entire `/src` directory, categorized by Logic, Performance, Security, and Maintenance issues.

---

## 1. Logic Bugs

#### 🐞 **Issue: Flawed Filter Logic & Uncontrolled Component State**
- **Files**: `src/components/Filter/Filter.tsx`, `src/commons/Checkbox/Checkbox.tsx`
- **Analysis**:
  1.  The `Checkbox` component is **uncontrolled**. It maintains its own `isChecked` state internally. The parent `Filter` component has no direct knowledge or control over whether a checkbox is checked; it only listens for the `handleOnChange` event. This can lead to the UI becoming out of sync with the application state.
  2.  In `Filter.tsx`, `selectedCheckboxes` is a `Set` that is re-created from props (`filters`) on every single render. The `toggleCheckbox` function then mutates this *local copy*. This logic only works by chance because it immediately calls `filterProducts`, which triggers a context update and a re-render with the new `filters` prop. This is a fragile and incorrect way to manage state.
- **Impact**: Can lead to unpredictable UI behavior and state synchronization issues.

#### 🐞 **Issue: Negative or Zero Quantity Potential in Cart**
- **File**: `src/contexts/cart-context/useCartProducts.ts`
- **Functions**: `decreaseProductQuantity`, `updateQuantitySafely`
- **Analysis**: The core logic allows an item's quantity to be reduced to 0 or negative. An item with a quantity of 0 is not automatically removed from the cart, leaving the cart in an invalid state with "ghost" products. Business logic should be self-contained and enforce that an item is removed if its quantity falls below 1.
- **Impact**: The cart can hold invalid data, affecting counts, totals, and display logic.

#### 🐞 **Issue: Null Pointer Potential**
- **File**: `src/contexts/cart-context/useCartProducts.ts`, `src/contexts/products-context/useProducts.tsx`
- **Analysis**: Functions exported from hooks (`addProduct`, `removeProduct`, `filterProducts`) do not validate their arguments. Passing `null` or a malformed object (e.g., a product without an `.id`) will cause a runtime crash.
- **Impact**: Risk of application crashes from unexpected data.

---

## 2. Performance Bugs

#### 🐞 **Issue: Widespread Lack of Memoization**
- **Files**: `useCartProducts.ts`, `useProducts.tsx`, `useCartTotal.ts`, `Filter.tsx`, etc.
- **Analysis**: This is the most critical performance issue in the codebase. **Virtually no functions are memoized with `useCallback`**. This means new instances of `addProduct`, `filterProducts`, `toggleCheckbox`, etc., are created on every render. When these are passed as props, they break the memoization of child components (`React.memo`), forcing the entire component tree to re-render unnecessarily.
- **Impact**: Significant performance degradation, especially as the application scales. Causes excessive re-renders and computations.

#### 🐞 **Issue: Inefficient Filtering Algorithm**
- **File**: `src/contexts/products-context/useProducts.tsx`
- **Function**: `filterProducts`
- **Analysis**: The filter logic is highly inefficient for two reasons:
  1.  It re-fetches all products from the "API" every time a filter is applied.
  2.  The filter itself uses a nested `find-inside-find` pattern, which is less performant than other methods (e.g., creating a `Set` from the filters for quick lookups).
- **Impact**: Slows down the application and makes unnecessary network requests, leading to a poor user experience.

#### 🐞 **Issue: Redundant Computations in Cart Total**
- **File**: `src/contexts/cart-context/useCartTotal.ts`
- **Function**: `updateCartTotal`
- **Analysis**: This function performs three separate `.reduce()` operations over the entire products array every time the cart is updated. These calculations are not memoized with `useMemo`, meaning they run even if the underlying data hasn't changed in a way that would affect them.
- **Impact**: Wasted CPU cycles on every cart interaction.

---

## 3. Security Bugs

#### 🐞 **Issue: Missing Input Validation**
- **File**: `src/contexts/cart-context/useCartProducts.ts`
- **Function**: `addProduct`
- **Analysis**: No validation is performed on the `newProduct` object. An object with a missing or non-numeric `price` could be added to the cart, resulting in `NaN` (Not a Number) values in the total.
- **Impact**: Data corruption in the application's state, leading to display errors and potential runtime bugs.

#### 🐞 **Issue: Potential Path Traversal (Low Risk)**
- **File**: `src/components/Products/Product/style.ts`
- **Analysis**: The component's style dynamically constructs an image path using `require` with a product `sku`: ``require(`static/products/${sku}-1-product.webp`)``. In this project, the `sku` is sourced from a safe local JSON. However, if the `sku` ever came from user input or a mutable data source, this pattern would be vulnerable to a Path Traversal attack, allowing an attacker to read arbitrary files from the server's file system.
- **Impact**: Low risk in the current context, but it represents a dangerous pattern that should be avoided.

---

## 4. Maintenance Bugs

#### 🐞 **Issue: Hardcoded Data**
- **File**: `src/components/Filter/Filter.tsx`
- **Analysis**: The `availableSizes` array is hardcoded. If the products from the API change and new sizes become available, a developer must remember to manually update this array. It should be derived dynamically from the products themselves.
- **Impact**: High risk of the UI becoming out of sync with the data, making the code brittle and hard to maintain.

#### 🐞 **Issue: Split and Inconsistent Business Logic**
- **Files**: `useCartProducts.ts` vs. `CartProduct.tsx`
- **Analysis**: The business rule for minimum quantity is split across two locations. The UI prevents the user from clicking "decrease," but the hook itself allows the quantity to become zero or negative. **Business logic must be centralized in the hook** to be the single source of truth.
- **Impact**: Makes the code difficult to reason about and refactor. Bugs can be easily re-introduced.

#### 🐞 **Issue: Missing Error Handling**
- **File**: `src/contexts/products-context/useProducts.tsx`
- **Function**: `fetchProducts`
- **Analysis**: The `getProducts().then(...)` call has no corresponding `.catch()` block. If the API call were to fail (e.g., network error), it would result in an unhandled promise rejection, which could crash the application or leave it in a broken state.
- **Impact**: The application is not resilient to external service failures.

#### 🐞 **Issue: Tight Coupling**
- **File**: `src/contexts/cart-context/useCartProducts.ts`
- **Analysis**: Every function (`addProduct`, `removeProduct`, etc.) is responsible for manually calling `updateCartTotal`. This couples the product update logic with the total calculation logic. A better, more decoupled pattern would be to have a `useEffect` hook that listens for changes to `products` and triggers the total calculation.
- **Impact**: Violates the Single Responsibility Principle and makes the code harder to change. 
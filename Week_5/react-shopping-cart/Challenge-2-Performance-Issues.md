# Performance Optimization Report: Product Filtering

This document provides a detailed analysis and optimization guide for the product fetching and filtering functionality within `useProducts.tsx`.

### Original Code (`useProducts.tsx`)

```typescript
import { useCallback } from 'react';
import { useProductsContext } from './ProductsContextProvider';
import { IProduct } from 'models';
import { getProducts } from 'services/products';

const useProducts = () => {
  const {
    isFetching,
    setIsFetching,
    products,
    setProducts,
    filters,
    setFilters,
  } = useProductsContext();

  const fetchProducts = useCallback(() => {
    setIsFetching(true);
    getProducts().then((products: IProduct[]) => {
      setIsFetching(false);
      setProducts(products);
    });
  }, [setIsFetching, setProducts]);

  const filterProducts = (filters: string[]) => {
    setIsFetching(true);
    getProducts().then((products: IProduct[]) => {
      setIsFetching(false);
      let filteredProducts;

      if (filters && filters.length > 0) {
        filteredProducts = products.filter((p: IProduct) =>
          filters.find((filter: string) =>
            p.availableSizes.find((size: string) => size === filter)
          )
        );
      } else {
        filteredProducts = products;
      }

      setFilters(filters);
      setProducts(filteredProducts);
    });
  };

  return {
    isFetching,
    fetchProducts,
    products,
    filterProducts,
    filters,
  };
};
```

---

## 1. Performance Bottlenecks Identified

- **Expensive Network Calls on Filter**: The most critical bottleneck is that `filterProducts` calls `getProducts()` every single time a filter is applied. This makes the UI slow and generates unnecessary network traffic. Data should be fetched once and then filtered on the client.
- **Lack of Memoization**: The `filterProducts` function is not wrapped in `useCallback`. This means a new function instance is created on every render of the component using this hook, which can cause unnecessary re-renders of child components.
- **Inefficient Filtering Algorithm**: The nested `.find()` logic (`filters.find(...).find(...)`) is not the most efficient way to check if a product matches the selected sizes.

---

## 2. Implementing Proper Memoization & Logic Optimization

The solution involves three key changes:
1.  **Store the master product list**: Introduce a new state variable (`allProducts`) to hold the original, unfiltered list of products.
2.  **Optimize `filterProducts`**: Rewrite the function to filter the local `allProducts` array instead of making a network call. Wrap it in `useCallback`.
3.  **Update `fetchProducts`**: Have `fetchProducts` populate both the master list (`allProducts`) and the initial displayed list (`products`).

### Corrected Code (`useProducts.tsx`)

```typescript
import { useState, useCallback } from 'react'; // Import useState
import { useProductsContext } from './ProductsContextProvider';
import { IProduct } from 'models';
import { getProducts } from 'services/products';

const useProducts = () => {
  const {
    isFetching,
    setIsFetching,
    products,      // This will now be the *filtered* list
    setProducts,
    filters,
    setFilters,
  } = useProductsContext();

  // ✅ 1. Store the master list of all products
  const [allProducts, setAllProducts] = useState<IProduct[]>([]);

  // ✅ 2. Update fetchProducts to populate both lists
  const fetchProducts = useCallback(() => {
    console.log('Fetching all products from server...');
    setIsFetching(true);
    getProducts().then((fetchedProducts: IProduct[]) => {
      setIsFetching(false);
      setAllProducts(fetchedProducts); // Store the master list
      setProducts(fetchedProducts);    // Set the initial displayed list
    });
  }, [setIsFetching, setProducts]); // Dependencies updated

  // ✅ 3. Optimize filterProducts
  const filterProducts = useCallback((newFilters: string[]) => {
    console.time('Filtering Performance'); // Start performance timer

    setFilters(newFilters);

    let filteredProducts;
    if (newFilters.length > 0) {
      // ✅ More efficient filtering logic
      filteredProducts = allProducts.filter((product) =>
        newFilters.some((filter) => product.availableSizes.includes(filter))
      );
    } else {
      // ✅ If no filters, show the master list
      filteredProducts = allProducts;
    }

    setProducts(filteredProducts);
    console.timeEnd('Filtering Performance'); // End performance timer
  }, [allProducts, setFilters, setProducts]); // Dependencies updated

  return {
    isFetching,
    fetchProducts,
    products,
    filterProducts,
    filters,
  };
};
```
*Note: You would need to add `allProducts` and `setAllProducts` to your `ProductsContextProvider`.*

---

## 4. Adding Performance Monitoring

You can directly measure the impact of these changes.

### Before vs. After: Network Calls
- **Before**: Open your browser's Network tab. Every time you click a size filter, you will see a new network request for `products.json`.
- **After**: The network request for `products.json` will only happen **once** when `fetchProducts` is first called. Subsequent filtering will cause no network activity.

### Before vs. After: Filtering Speed
You can measure the filtering speed using `console.time`.

**How to Test:**
1. Add `console.time("Filtering Performance");` to the beginning of the `filterProducts` function.
2. Add `console.timeEnd("Filtering Performance");` to the end of the `filterProducts` function.
3. **Run the "Before" code**: The console will log the time taken, which includes network latency (e.g., `50ms - 100ms` or more).
4. **Run the "After" code**: The console will now log only the time it takes for the client-side filtering to complete (e.g., `< 1ms`), demonstrating a massive improvement.

### Before vs. After: Re-renders (Memoization)
You can see the effect of `useCallback` by adding a log.

**How to Test:**
1.  In the original `useProducts.tsx`, add `console.log("filterProducts function was re-created");` inside the hook but before the `return` statement. You will see this log on *every render* of the parent component.
2.  In the corrected code, this log will only appear when the dependencies of `useCallback` (`allProducts`, `setFilters`, `setProducts`) actually change, preventing unnecessary re-renders of child components that depend on `filterProducts`. 
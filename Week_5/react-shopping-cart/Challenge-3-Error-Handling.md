# API Error Handling Analysis Report

This document outlines the implementation of robust error handling for the API calls in `getProducts` and `useProducts`.

---

## Original Code

### `src/services/products.ts`
```typescript
export const getProducts = async () => {
  let response: IGetProductsResponse;

  if (isProduction) {
    response = await axios.get(
      'https://react-shopping-cart-67954.firebaseio.com/products.json'
    );
  } else {
    response = require('static/json/products.json');
  }

  const { products } = response.data || [];
  return products;
};
```

### `src/contexts/products-context/useProducts.tsx`
```typescript
const useProducts = () => {
  // ...
  const fetchProducts = useCallback(() => {
    setIsFetching(true);
    getProducts().then((fetchedProducts: IProduct[]) => {
      setIsFetching(false);
      setAllProducts(fetchedProducts);
      setProducts(fetchedProducts);
    });
  }, [setIsFetching, setProducts]);
  // ...
};
```

---

## Issues Identified

1.  **No Error Handling**: The `getProducts` function lacks any `try/catch` blocks. If the `axios.get` promise rejects (due to a network error or a 4xx/5xx HTTP status), the application will have an unhandled promise rejection.
2.  **Stuck Loading States**: In `useProducts`, `setIsFetching(false)` is only called in the `.then()` block. If `getProducts()` fails, this line is never reached, and the UI could be stuck in a permanent loading state.
3.  **No User-Facing Messages**: There is no mechanism to catch errors and store them in a state that the UI can use to display a helpful message like "Could not connect to the server."
4.  **No Retry Mechanism**: For transient network errors, there is no logic to automatically retry the failed request.

---

## Corrected and Hardened Code

### 1. `src/services/products.ts` (Service Layer)

The service layer is now responsible for making the API call and translating any error into a consistent, user-friendly error message.

```typescript
import axios from 'axios';
import { IGetProductsResponse } from 'models';

const isProduction = process.env.NODE_ENV === 'production';

export const getProducts = async () => {
  // Local development data has minimal error handling
  if (!isProduction) {
    try {
      const response: IGetProductsResponse = require('static/json/products.json');
      return response.data?.products || [];
    } catch (e) {
      console.error('Failed to load local product data.', e);
      throw new Error(
        'Could not load local product data. Please check the file `static/json/products.json`.'
      );
    }
  }

  // Production data fetching with robust error handling
  try {
    const response = await axios.get(
      'https://react-shopping-cart-67954.firebaseio.com/products.json'
    );
    // Axios throws for non-2xx, so a successful response is guaranteed here.
    return response.data?.products || [];
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        // The server responded with a status code outside the 2xx range
        console.error('API Error:', error.response.status, error.response.data);
        throw new Error(
          `We're having trouble fetching products (Status: ${error.response.status}). Please try again later.`
        );
      } else if (error.request) {
        // The request was made but no response was received (e.g., network error)
        console.error('Network Error:', error.request);
        throw new Error(
          'Cannot connect to the server. Please check your internet connection.'
        );
      }
    }
    // A non-axios or unexpected error occurred
    console.error('Unexpected Error:', error);
    throw new Error('An unexpected error occurred while fetching products.');
  }
};
```

### 2. `src/contexts/products-context/ProductsContextProvider.tsx` (Context Layer)

The context is updated to track error state globally.

```typescript
export interface IProductsContext {
  // ... existing
  error: string | null;
  setError(error: string | null): void;
}

const ProductsProvider: FC = (props) => {
  // ... existing states
  const [error, setError] = useState<string | null>(null);

  const ProductContextValue: IProductsContext = {
    // ... existing values
    error,
    setError,
  };
  //...
};
```

### 3. `src/contexts/products-context/useProducts.tsx` (Hook/Logic Layer)

The hook now handles the side effects of the API call, updating loading and error states.

```typescript
const useProducts = () => {
  const {
    // ...
    error,
    setError,
  } = useProductsContext();
  // ...

  const fetchProducts = useCallback(async () => {
    setIsFetching(true);
    setError(null); // Reset error state on new fetch
    try {
      const fetchedProducts = await getProducts();
      setAllProducts(fetchedProducts || []); // Ensure data is always an array
      setProducts(fetchedProducts || []);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'An unknown error occurred.';
      setError(errorMessage);
      // Clear out any stale product data on error
      setProducts([]);
      setAllProducts([]);
    } finally {
      // ✅ This block runs regardless of success or failure
      setIsFetching(false);
    }
  }, [setIsFetching, setProducts, setError, setAllProducts]); // Added dependencies

  return {
    isFetching,
    fetchProducts,
    products,
    filterProducts,
    filters,
    error, // Return error for convenience
  };
};
```

---

## How the Solution Addresses the Criteria

1.  **Comprehensive `try-catch` blocks**: Both `getProducts` and `fetchProducts` now use `try/catch` to handle promise rejections gracefully. `fetchProducts` also uses a `finally` block.
2.  **Network error handling**: `getProducts` now uses `axios.isAxiosError` and checks for `error.request` to specifically identify and handle network errors, providing a clear message.
3.  **HTTP status code validation**: The `error.response` check in `getProducts` handles non-2xx status codes, extracting the status and providing a relevant error message.
4.  **User-friendly error messages**: The service layer generates clear messages, and the context layer stores them in a state (`error`). A UI component can now easily consume this state:
    ```jsx
    const { error, isFetching } = useProducts();
    // ...
    if (error) return <p>Error: {error}</p>;
    if (isFetching) return <Loader />;
    ```
5.  **Retry mechanisms for failed requests**: This is a powerful pattern for handling transient errors. While not implemented directly to keep the code clean, it can be easily added to `getProducts`. Here is a production-ready example using a simple loop:
    ```typescript
    // Example of getProducts with a retry mechanism
    async function getProductsWithRetry(retries = 3, delayMs = 500) {
      for (let i = 0; i < retries; i++) {
        try {
          // Attempt to fetch...
          return await getProducts();
        } catch (error) {
          // If it's the last attempt, throw the error
          if (i === retries - 1) throw error;
          // Wait before the next attempt
          await new Promise(res => setTimeout(res, delayMs));
        }
      }
    }
    ```
    For more complex scenarios, a library like `axios-retry` is recommended.

6.  **Loading states management**: The `finally` block in `fetchProducts` guarantees that `setIsFetching(false)` is always executed, whether the API call succeeds or fails. This prevents the UI from getting stuck in an infinite loading state. 
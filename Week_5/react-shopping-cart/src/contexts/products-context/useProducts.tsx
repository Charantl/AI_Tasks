import { useState, useCallback } from 'react';

import { useProductsContext } from './ProductsContextProvider';
import { IProduct } from 'models';
import { getProducts } from 'services/products';

/**
 * A custom hook for managing product fetching and filtering logic.
 *
 * @returns An object containing product data, state, and action functions.
 * @property {boolean} isFetching - True if products are being fetched.
 * @property {function} fetchProducts - An async function to fetch all products from the service.
 * @property {IProduct[]} products - The current, possibly filtered, list of products.
 * @property {function} filterProducts - Function to filter the products based on an array of size strings.
 * @property {string[]} filters - The array of currently applied filters.
 * @property {string | null} error - An error message if the fetch fails, otherwise null.
 */
const useProducts = () => {
  const {
    isFetching,
    setIsFetching,
    products,
    setProducts,
    filters,
    setFilters,
    allProducts,
    setAllProducts,
    error,
    setError,
  } = useProductsContext();

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
      
      // TODO: Integrate with an error reporting service like Sentry, LogRocket, etc.
      // Example: Sentry.captureException(err);

      setError(errorMessage);
      // Clear out any stale product data on error
      setProducts([]);
      setAllProducts([]);
    } finally {
      // This block runs regardless of success or failure
      setIsFetching(false);
    }
  }, [setIsFetching, setProducts, setError, setAllProducts]);

  const filterProducts = useCallback(
    (newFilters: string[]) => {
      setFilters(newFilters);

      let filteredProducts;
      if (newFilters.length > 0) {
        filteredProducts = allProducts.filter((product) =>
          newFilters.some((filter) => product.availableSizes.includes(filter))
        );
      } else {
        filteredProducts = allProducts;
      }

      setProducts(filteredProducts);
    },
    [allProducts, setFilters, setProducts]
  );

  return {
    isFetching,
    fetchProducts,
    products,
    filterProducts,
    filters,
    error, // Return error for convenience
  };
};

export default useProducts;

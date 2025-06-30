import { createContext, useContext, FC, useState, ReactNode } from 'react';

import { IProduct } from 'models';

export interface IProductsContext {
  isFetching: boolean;
  setIsFetching(state: boolean): void;
  products: IProduct[];
  setProducts(products: IProduct[]): void;
  filters: string[];
  setFilters(filters: string[]): void;
  allProducts: IProduct[];
  setAllProducts(products: IProduct[]): void;
  error: string | null;
  setError(error: string | null): void;
}

/**
 * ProductsContext
 *
 * This context is responsible for managing the state of products,
 * including fetching status, filtering, and error handling.
 *
 * @property {boolean} isFetching - True if products are currently being fetched.
 * @property {function} setIsFetching - Setter for the fetching state.
 * @property {IProduct[]} products - The filtered list of products to be displayed.
 * @property {function} setProducts - Setter for the displayed products.
 * @property {string[]} filters - The currently applied size filters.
 * @property {function} setFilters - Setter for the filters.
 * @property {IProduct[]} allProducts - The master, unfiltered list of all products.
 * @property {function} setAllProducts - Setter for the master products list.
 * @property {string | null} error - A string containing an error message if an API call fails, otherwise null.
 * @property {function} setError - Setter for the error state.
 */
const ProductsContext = createContext<IProductsContext | undefined>(undefined);

/**
 * Custom hook to use the ProductsContext.
 * Ensures that the hook is used within a component tree wrapped by ProductsProvider.
 * @returns {IProductsContext} The context values.
 */
const useProductsContext = (): IProductsContext => {
  const context = useContext(ProductsContext);

  if (!context) {
    throw new Error(
      'useProductsContext must be used within a ProductsProvider'
    );
  }

  return context;
};

/**
 * Provider component for the ProductsContext.
 * It supplies the product-related state and setters to its children.
 */
const ProductsProvider: FC<{ children: ReactNode }> = ({ children }) => {
  const [isFetching, setIsFetching] = useState(false);
  const [products, setProducts] = useState<IProduct[]>([]);
  const [filters, setFilters] = useState<string[]>([]);
  const [allProducts, setAllProducts] = useState<IProduct[]>([]);
  const [error, setError] = useState<string | null>(null);

  const ProductContextValue: IProductsContext = {
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
  };

  return (
    <ProductsContext.Provider value={ProductContextValue}>
      {children}
    </ProductsContext.Provider>
  );
};

export { ProductsProvider, useProductsContext };

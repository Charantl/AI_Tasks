import { useCartContext } from './CartContextProvider';
import useCartTotal from './useCartTotal';
import { ICartProduct } from 'models';

/**
 * A custom hook to manage all product-related actions in the shopping cart.
 *
 * @returns An object containing the cart products and functions to manipulate them.
 * @property {ICartProduct[]} products - The array of products currently in the cart.
 * @property {function} addProduct - Function to add a new product or increase its quantity.
 * @property {function} removeProduct - Function to remove a product from the cart.
 * @property {function} increaseProductQuantity - Function to increase a product's quantity by 1.
 * @property {function} decreaseProductQuantity - Function to decrease a product's quantity by 1.
 */
const useCartProducts = () => {
  const { products, setProducts } = useCartContext();
  const { updateCartTotal } = useCartTotal();

  const updateQuantitySafely = (
    currentProduct: ICartProduct,
    targetProduct: ICartProduct,
    quantity: number
  ): ICartProduct => {
    if (currentProduct.id === targetProduct.id) {
      return Object.assign({
        ...currentProduct,
        quantity: currentProduct.quantity + quantity,
      });
    } else {
      return currentProduct;
    }
  };

  const addProduct = (newProduct: ICartProduct) => {
    let updatedProducts;
    const isProductAlreadyInCart = products.some(
      (product: ICartProduct) => newProduct.id === product.id
    );

    if (isProductAlreadyInCart) {
      updatedProducts = products.map((product: ICartProduct) => {
        if (product.id === newProduct.id) {
          return {
            ...product,
            quantity: product.quantity + newProduct.quantity,
          };
        }
        return product;
      });
    } else {
      updatedProducts = [...products, newProduct];
    }

    setProducts(updatedProducts);
    updateCartTotal(updatedProducts);
  };

  const removeProduct = (productToRemove: ICartProduct) => {
    const updatedProducts = products.filter(
      (product: ICartProduct) => product.id !== productToRemove.id
    );

    setProducts(updatedProducts);
    updateCartTotal(updatedProducts);
  };

  const increaseProductQuantity = (productToIncrease: ICartProduct) => {
    const updatedProducts = products.map((product: ICartProduct) => {
      return updateQuantitySafely(product, productToIncrease, +1);
    });

    setProducts(updatedProducts);
    updateCartTotal(updatedProducts);
  };

  const decreaseProductQuantity = (productToDecrease: ICartProduct) => {
    const updatedProducts = products.map((product: ICartProduct) => {
      return updateQuantitySafely(product, productToDecrease, -1);
    });

    setProducts(updatedProducts);
    updateCartTotal(updatedProducts);
  };

  return {
    products,
    addProduct,
    removeProduct,
    increaseProductQuantity,
    decreaseProductQuantity,
  };
};

export default useCartProducts;

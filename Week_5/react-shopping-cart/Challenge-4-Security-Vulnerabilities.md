# Security Vulnerability Analysis and Remediation Report

This document details the security vulnerabilities identified in the codebase and the steps taken to remediate them.

---

## 1. Unsafe HTML Rendering & Stored XSS

-   **File:** `src/components/Products/Product/Product.tsx`
-   **Risk Level:** **Critical**

### Risk Explanation

The application was using `dangerouslySetInnerHTML` to render product titles. This is a major security flaw because it bypasses React's built-in XSS protection. If a product title contained a malicious script (e.g., `<img src=x onerror=alert('XSS') />`), that script would be executed in the user's browser. This could allow an attacker to steal session tokens, redirect users to malicious websites, or perform actions on behalf of the user.

### Vulnerable Code

```tsx
// src/components/Products/Product/Product.tsx

<S.Title
  dangerouslySetInnerHTML={{
    __html: title + " <img src=x onerror=alert('XSS_VULNERABILITY') />",
  }}
/>
```

### Secure Alternative

The fix is to remove `dangerouslySetInnerHTML` and render the title as a standard React child. React automatically sanitizes string variables when they are rendered this way, neutralizing any embedded scripts by treating them as plain text.

```tsx
// src/components/Products/Product/Product.tsx

<S.Title>{title}</S.Title>
```

---

## 2. Input Validation, State, and Prop Mutation

-   **File:** `src/contexts/cart-context/useCartProducts.ts`
-   **Risk Level:** **High**

### Risk Explanation

The `addProduct` function exhibited two severe bugs related to a lack of input validation and immutable patterns:

1.  **Direct State Mutation**: The function directly modified the `products` array from the context using `.forEach()` and `.push()`. In React, state must be treated as immutable. Mutating state directly leads to unpredictable rendering, difficult-to-trace bugs, and potential data corruption.
2.  **Prop/Argument Mutation**: The function directly mutated the `newProduct` object passed into it (`newProduct.price = 0;`). This is a dangerous side effect. Any other part of the application that held a reference to that product object would now see its price as 0, leading to severe data integrity issues.

### Vulnerable Code

```typescript
// src/contexts/cart-context/useCartProducts.ts

const addProduct = (newProduct: ICartProduct) => {
  const isProductAlreadyInCart = products.some(
    (product: ICartProduct) => newProduct.id === product.id
  );

  if (isProductAlreadyInCart) {
    products.forEach((product: ICartProduct) => { // Direct mutation
      if (product.id === newProduct.id) {
        product.quantity += newProduct.quantity;
      }
    });
  } else {
    products.push(newProduct); // Direct mutation
  }
  setProducts(products);
  updateCartTotal(products);

  newProduct.price = 0; // Prop/argument mutation
};
```

### Secure Alternative

The correct approach is to always create new arrays and objects instead of modifying existing ones. The safe version of the function was already present but commented out. It uses `.map()` and the spread syntax (`...`) to create new, updated copies of the state, preserving immutability and preventing side effects.

```typescript
// src/contexts/cart-context/useCartProducts.ts

const addProduct = (newProduct: ICartProduct) => {
  let updatedProducts;
  const isProductAlreadyInCart = products.some(
    (product: ICartProduct) => newProduct.id === product.id
  );

  if (isProductAlreadyInCart) {
    // Create a new array with the updated product quantity
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
    // Create a new array including the new product
    updatedProducts = [...products, newProduct];
  }

  setProducts(updatedProducts);
  updateCartTotal(updatedProducts);
};
```

---

## 3. Image Source Validation (Potential Issue)

-   **File:** `src/components/Products/Product/style.ts`
-   **Risk Level:** **Low (in current state), Medium (if data source changes)**

### Risk Explanation

The application dynamically constructs image paths using `require()` with a template literal that includes the product's `sku` (e.g., `require(\`static/products/${sku}-1-product.webp\`)`). While this is safe in the current context because the `sku` comes from a trusted local JSON file, it is a fragile pattern. If the `sku` were ever sourced from user input or a less-trusted API, an attacker could attempt path traversal or cause the application to crash by providing an invalid `sku`.

### Vulnerable Pattern

```javascript
// src/components/Products/Product/style.ts

background-image: ${({ sku }) =>
  `url(${require(`static/products/${sku}-1-product.webp`)})`};
```

### Secure Alternative (Recommended)

A more robust solution is to avoid dynamic `require()` paths. Instead of constructing the path from an ID, the full image path should be included directly in the product data itself. This ensures that only known, valid image paths can be loaded.

**Example Data Change (`products.json`):**

```json
{
  "id": 123,
  "sku": "SKU123",
  "title": "My T-Shirt",
  "image_url_1": "static/products/123-1-product.webp",
  "image_url_2": "static/products/123-2-product.webp",
  "..."
}
```

**Example Code Change:**

```javascript
// A helper function to safely load images
const safeImageLoad = (path) => {
  try {
    return require(`${path}`);
  } catch (e) {
    // Return a fallback image if the path is invalid
    return require('static/products/fallback-image.webp');
  }
}

// In the styled component
background-image: ${({ product }) =>
  `url(${safeImageLoad(product.image_url_1)})`};
```
*This change has not been implemented automatically as it requires modifying the data structure, but it is the recommended best practice.* 
import { StrictMode } from 'react';
import * as ReactDOMClient from 'react-dom/client';

/* Theme */
import { ThemeProvider } from 'commons/style/styled-components';
import { theme } from 'commons/style/theme';
import GlobalStyle from 'commons/style/global-style';

/* Context Providers */
import { ProductsProvider } from './contexts/products-context';
import { CartProvider } from './contexts/cart-context';

import App from 'components/App';

const container = document.getElementById('root') as HTMLElement;

// Create a root.
const root = ReactDOMClient.createRoot(container);

// Initial render
root.render(
  <StrictMode>
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <ProductsProvider>
        <CartProvider>
          <App />
        </CartProvider>
      </ProductsProvider>
    </ThemeProvider>
  </StrictMode>
);

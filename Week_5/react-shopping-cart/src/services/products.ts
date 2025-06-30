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
      process.env.REACT_APP_API_URL || 'https://react-shopping-cart-67954.firebaseio.com/products.json'
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

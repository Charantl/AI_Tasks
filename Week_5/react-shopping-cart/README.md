# React Shopping Cart

[![Netlify Status](https://api.netlify.com/api/v1/badges/a11e5d4b-352c-4573-add3-94c6553895e6/deploy-status)](https://app.netlify.com/sites/react-shopping-cart-plus/deploys)

> A simple shopping cart application built with React.

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).

![demo](https://raw.githubusercontent.com/jeffersonRibeiro/react-shopping-cart/master/readme-banner.png)

## Features

-   Add/remove products from the cart
-   Filter products by size
-   Responsive design

## Project Setup and Usage

### Prerequisites

-   Node.js (v14 or newer)
-   npm

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/jeffersonRibeiro/react-shopping-cart.git
    ```
2.  Navigate to the project directory:
    ```bash
    cd react-shopping-cart
    ```
3.  Install dependencies:
    ```bash
    npm install
    ```

### Available Scripts

In the project directory, you can run:

#### `npm start`

Runs the app in the development mode.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br />
You will also see any lint errors in the console.

#### `npm test`

Launches the test runner in the interactive watch mode.

#### `npm run build`

Builds the app for production to the `build` folder.<br />
It correctly bundles React in production mode and optimizes the build for the best performance.

---

## Architectural Overview

The application follows a standard React component architecture with a clear separation of concerns.

-   **/src/components**: Contains all the UI components of the application. Each component is self-contained in its own folder with its styles and tests.
-   **/src/contexts**: Manages the global state of the application using the Context API.
    -   `products-context`: Handles fetching, filtering, and storing product data.
    -   `cart-context`: Manages the state of the shopping cart, including adding, removing, and updating products.
-   **/src/services**: Responsible for all external API interactions. The `products.ts` service handles fetching product data from the backend.
-   **/src/static**: Contains static assets like images and the local `products.json` file used for development.

## Basic Overview - [Live Demo](https://react-shopping-cart-67954.firebaseapp.com/)

<p align="left">

  <img src="./work-in-the-netherlands.png" width="380" height="90">
</p>

✈️ [Follow Jeremy Akeze](https://www.linkedin.com/in/jeremy-akeze-9542b396/)

This simple shopping cart prototype shows how React with Typescript, React hooks, react Context and Styled Components can be used to build a friendly user experience with instant visual updates and scaleable code in ecommerce applications.

#### Features

- Add and remove products from the floating cart using Context Api
- Filter products by available sizes using Context Api
- Responsive design

<!--
## Getting started

Try playing with the code on CodeSandbox :)

[![Edit app](https://codesandbox.io/static/img/play-codesandbox.svg)](https://codesandbox.io/s/74rykw70qq)
 -->

## Build/Run

#### Requirements

- Node.js
- NPM

```javascript

/* First, Install the needed packages */
npm install

/* Then start the React app */
npm start

/* To run the tests */
npm run test

```

### Copyright and license

The MIT License (MIT). Please see License File for more information.

<br/>
<br/>

<p align="center"><img src="http://www.jeffersonribeiro.com/assets/img/apple-icon-180x180.png" width="35" height="35"/></p>
<p align="center">
<sub>A little project by <a href="http://www.jeffersonribeiro.com/">Jefferson Ribeiro</a></sub>
</p>

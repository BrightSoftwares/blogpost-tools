# E-Commerce Templates for Jekyll Sites

This directory contains templates for adding e-commerce functionality to Jekyll sites using Stripe for payments.

## Features

- **Cart Management**: LocalStorage-based cart with real-time UI updates
- **Stripe Integration**: Secure payment processing with Stripe Checkout
- **Cash on Delivery**: Alternative payment method for local deliveries
- **Product Collections**: Jekyll collection-based product management
- **Multi-currency Support**: Configurable currency display

## Quick Setup

### 1. Add Stripe Configuration to `_config.yml`

```yaml
# E-Commerce Settings
stripe_publishable_key: "pk_live_your_key_here"  # Use pk_test_ for testing
currency: "XOF"  # or EUR, USD, etc.
currency_symbol: "XOF"

# Product collection
collections:
  products:
    output: true
    permalink: /products/:slug/

# Free shipping threshold (optional)
free_shipping_threshold: 50000
```

### 2. Copy Required Files

```bash
# Copy cart.js to your assets
cp cart.js your-site/assets/js/

# Add checkout page
cp checkout.html your-site/

# Add product layout
cp _layouts/product.html your-site/_layouts/
```

### 3. Create Products Collection

Create `_products/` directory and add products as markdown files:

```yaml
---
title: "Product Name"
slug: "product-name"
price: 2000
sale_price: 1500  # optional
images:
  - /assets/images/products/product-1.jpg
  - /assets/images/products/product-2.jpg
categories:
  - Category Name
stock_status: instock  # or outofstock
stripe_price_id: "price_xxxxx"  # from Stripe Dashboard
description: "Product description here"
---

Extended product content in markdown...
```

### 4. Include Cart Script

Add to your layout's `<head>` or before `</body>`:

```html
<script src="/assets/js/cart.js"></script>
```

### 5. Add Cart Display (Header)

```html
<div class="cart-icon">
  <a href="/cart.html">
    <i class="fa fa-shopping-cart"></i>
    <span id="cart-qty" class="cart-count">0</span>
  </a>
</div>
```

### 6. Add to Cart Button (Product Page)

```html
<button onclick="addToCart(
  '{{ page.stripe_price_id }}',
  '{{ page.title }}',
  {{ page.price }},
  '{{ page.images.first }}',
  '{{ page.slug }}'
)" class="btn btn-add-to-cart">
  Add to Cart
</button>
```

## Stripe Setup

1. Create a Stripe account at https://stripe.com
2. Go to Developers > API keys
3. Copy your **Publishable key** to `_config.yml`
4. Create products in Stripe Dashboard
5. Copy the **Price ID** for each product to your product markdown files

### Environment Variables for Netlify

For server-side operations (webhooks, session creation), set these in Netlify:

```
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
```

## Shipping Configuration

Configure shipping zones in `checkout.html`:

```javascript
const SHIPPING_ZONES = [
  { value: "zone-1", label: "Zone 1", cost: 2000 },
  { value: "zone-2", label: "Zone 2", cost: 3500 },
  { value: "zone-3", label: "Zone 3", cost: 5000 }
];
```

## Customization

### Currency

Change the `CURRENCY` constant in `cart.js`:

```javascript
const CURRENCY = 'EUR'; // or 'USD', 'XOF', etc.
```

### Notifications

Customize notification styles in the `showNotification()` function.

### Checkout Flow

For Stripe Checkout sessions, you'll need a serverless function.
See `netlify-functions/` for examples.

## Files Structure

```
your-site/
├── _config.yml           # Add Stripe keys here
├── _products/            # Product collection
│   ├── product-1.md
│   └── product-2.md
├── _layouts/
│   └── product.html      # Product page layout
├── _data/
│   └── stripe_products.json  # Synced from Stripe (optional)
├── assets/
│   └── js/
│       └── cart.js       # Cart management
├── cart.html             # Cart page
├── checkout.html         # Checkout page
└── success.html          # Order confirmation
```

## Security Notes

- Never commit your `STRIPE_SECRET_KEY` to version control
- Always use environment variables for sensitive keys
- Use `pk_test_` keys during development
- Validate cart contents server-side before processing payments

## Support

For issues or feature requests, open an issue in the blogpost-tools repository.

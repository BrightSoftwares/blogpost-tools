// E-Commerce Cart Management for Jekyll Sites
// Compatible with Stripe checkout integration
(function() {
    'use strict';

    const CART_KEY = 'cart';
    const CURRENCY = 'XOF'; // Change to your currency (EUR, USD, etc.)

    // Get cart from localStorage
    function getCart() {
        return JSON.parse(localStorage.getItem(CART_KEY) || '[]');
    }

    // Save cart to localStorage
    function saveCart(cart) {
        localStorage.setItem(CART_KEY, JSON.stringify(cart));
    }

    // Update cart display in header
    function updateCartDisplay() {
        const cart = getCart();
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        const totalPrice = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

        // Update cart count elements
        const cartQtyElements = document.querySelectorAll('#cart-qty, .cart-count, .minicart-qty');
        cartQtyElements.forEach(el => {
            if (el) el.textContent = totalItems;
        });

        // Update cart total
        const cartTotalElement = document.getElementById('cart-total');
        if (cartTotalElement) {
            cartTotalElement.textContent = formatPrice(totalPrice);
        }

        updateCartDropdown(cart);
    }

    // Format price with currency
    function formatPrice(amount) {
        return Math.round(amount).toLocaleString() + ' ' + CURRENCY;
    }

    // Update cart dropdown
    function updateCartDropdown(cart) {
        const cartItemsContainer = document.getElementById('cart-items');
        if (!cartItemsContainer) return;

        if (cart.length === 0) {
            cartItemsContainer.innerHTML = '<li><p class="text-center">Your cart is empty</p></li>';
        } else {
            let html = '';
            cart.forEach(item => {
                html += `
                    <li class="pr-cart-item">
                        <div class="product-image">
                            <figure><img src="${item.image || '/assets/images/placeholder.png'}" alt="${item.name}" width="90" height="90"></figure>
                        </div>
                        <div class="product-info">
                            <a href="/products/${item.slug}/" class="product-name">${item.name}</a>
                            <div class="price">
                                <span class="quantity">${item.quantity} x </span>
                                <span class="price-amount">${formatPrice(item.price)}</span>
                            </div>
                        </div>
                        <div class="delete-item">
                            <a href="#" class="btn-remove" onclick="removeFromCart('${item.priceId}'); return false;">
                                <i class="fa fa-times"></i>
                            </a>
                        </div>
                    </li>
                `;
            });
            cartItemsContainer.innerHTML = html;
        }

        // Update total
        const totalPrice = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        const totalElements = document.querySelectorAll('.minicart-total, .sub-total');
        totalElements.forEach(el => {
            el.textContent = formatPrice(totalPrice);
        });
    }

    // Add item to cart
    window.addToCart = function(priceId, name, price, image, slug) {
        if (!priceId) {
            showNotification('Product not available', 'error');
            return;
        }

        let cart = getCart();
        const existingItem = cart.find(item => item.priceId === priceId);

        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            cart.push({
                priceId: priceId,
                name: name,
                price: parseFloat(price),
                image: image,
                slug: slug,
                quantity: 1
            });
        }

        saveCart(cart);
        updateCartDisplay();
        showNotification(`"${name}" added to cart!`, 'success');
    };

    // Remove item from cart
    window.removeFromCart = function(priceId) {
        let cart = getCart();
        cart = cart.filter(item => item.priceId !== priceId);
        saveCart(cart);
        updateCartDisplay();
        showNotification('Item removed from cart', 'info');
    };

    // Update cart item quantity
    window.updateCartQuantity = function(priceId, quantity) {
        let cart = getCart();
        const item = cart.find(item => item.priceId === priceId);

        if (item) {
            if (quantity <= 0) {
                removeFromCart(priceId);
            } else {
                item.quantity = quantity;
                saveCart(cart);
                updateCartDisplay();
            }
        }
    };

    // Clear cart
    window.clearCart = function() {
        saveCart([]);
        updateCartDisplay();
        showNotification('Cart cleared', 'info');
    };

    // Get cart (global)
    window.getCart = getCart;

    // Show notification
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification-toast alert alert-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 99999;
            min-width: 300px;
            padding: 15px 20px;
            border-radius: 5px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideIn 0.3s ease-in-out;
            background-color: ${type === 'error' ? '#f44336' : type === 'warning' ? '#ff9800' : type === 'success' ? '#4caf50' : '#2196f3'};
            color: white;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-in-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Initialize
    document.addEventListener('DOMContentLoaded', function() {
        updateCartDisplay();
        setInterval(updateCartDisplay, 5000);
    });

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
})();

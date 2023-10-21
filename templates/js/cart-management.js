couponCodes = {
  'entery10': 0.1,
  'nice15': 0.15,
  'super20': 0.2,
  'vip40': 0.4
}

let itemsIndex = {};
let numItemsInCart = 0;
let cart = [];


function loadCart() {
  const storedCart = JSON.parse(localStorage.getItem('cart'));

  if (storedCart) {
    cart = storedCart;
    order['items'] = cart;

    const cartCounter = document.getElementById('cart-counter');
    cartCounter.innerText = cart.length;

    cart.forEach(item => {
      itemsIndex[item.item_id] = true;
      addItemRowtoUI(item);
      updateOrderTotal(item.quantity, item.price, 'add');
    });
  }
}


function findItemIndex(itemId) {
  if (itemsIndex.hasOwnProperty(itemId)) {
    return cart.findIndex((item) => item.item_id === itemId);
  }
  return -1
}

function updateCart(updatedCart) {
  localStorage.setItem('cart', JSON.stringify(updatedCart));
  order['items'] = updatedCart;
  cart = updatedCart;
}

function clearCart() {
  localStorage.setItem('cart', JSON.stringify([]));
  cart = [];
  numItemsInCart = 0;
  itemsIndex = {};
  order['items'] = [];
  order['amount_paid'] = 0;
  order['total_cost'] = 0;
  order['discount'] = 0;

  const cartList = document.querySelector('.items-body');
  cartList.innerHTML = '';

  const order_total_text = document.getElementById('total-price');
  order_total_text.innerHTML = "Total: $0";

  const cartCounter = document.getElementById('cart-counter');
  cartCounter.innerText = "0";
}

function removeFromCart(itemId) {
  const index = findItemIndex(itemId);
  const itemData = cart[index];
  console.log(itemData)
  // Delete the item
  filteredCart = cart.filter((itemData) => itemData.item_id !== itemId);

  // If cart is now empty
  if (filteredCart.length === 0) {
    clearCart();
    return;
  }

  updateCart(filteredCart);
  delete itemsIndex[itemId];

  // Deduct ordered item from the total price
  updateOrderTotal(itemData['quantity'], itemData['price'], 'remove');

  const itemRow = document.getElementById(`cart-row-item-${itemId}`);
  if (itemRow) {
      itemRow.remove();
  }

  const cartIcon = document.getElementById('cart-counter');
  cartIcon.innerText = cart.length;

  console.log(order['total_cost']);

  return;
}


function addToCart(itemId) {
  let item = {};

  if (itemsIndex.hasOwnProperty(itemId)) {
      // Find the index of the item to update
      const index = findItemIndex(itemId);
      
    // Check if the item exists in the cart
    if (cart[index]) {
      const quantity = Number(document.getElementById(`item-${itemId}`).querySelector('#quantity').value);

      // Update the quantity of the item at the specified index
      cart[index].quantity += quantity;
      item = {
        'item_id': itemId,
        'quantity': quantity,
        'price': cart[index].price
      };
    }

  } else {
    itemElement = document.getElementById(`item-${itemId}`);
    if (itemElement) {
      item = {
        'item_id': itemId,
        'item_name': itemElement.querySelector('#item-name').innerText,
        'quantity': Number(itemElement.querySelector('#quantity').value),
        'price': Number(
          itemElement.querySelector('#item-price').innerText.match(/(\d+\.?\d*)/)[0]
        )
      }
        console.log(`the items price: ${item.price}`);
        cart.push(item);
  
        itemsIndex[itemId] = true;
        
        const cartIcon = document.getElementById('cart-counter');
        cartIcon.innerText = cart.length;
    } else {
      // Item Id doesn't exist and thus nothing should be done.
      return;
    }
  }

  updateOrderTotal(item['quantity'], item['price'], 'add');
  updateCart(cart);
  addItemRowtoUI(item);

  console.log(order['total_cost']);
  console.log(order);
}


  function addItemRowtoUI(item) {
  // If adding to an item that already exists in the cart
  const existingItemRow =document.querySelector(`#cart-row-item-${item.item_id} #item-quantity`);
  if (existingItemRow) {
    existingItemRow.textContent = Number(existingItemRow.textContent) + item.quantity;
    return;
  } else {
      const newRow = document.createElement("tr");
      newRow.setAttribute("id", `cart-row-item-${item.item_id}`);
      newRow.innerHTML = `
      <td class="item-name">${item.item_name}</td>
      <td>$${item.price}</td>
      <td id="item-quantity">${item.quantity}</td>
      <td>
        <button class="item-remove-button" onclick="removeFromCart('${item.item_id}')">X</button>
      </td>`;

    // Insert the new row at the end of the table.
    const tableBody = document.querySelector(".cart-items tbody");
    tableBody.appendChild(newRow);
    return;
  }
}

function updateOrderTotal(quantity, price, operation) {
  discount = order['discount'];

  if (operation === 'add') {
      order['total_cost'] +=  quantity * price;
  }
  else {
      order['total_cost'] -=  quantity * price;
  }

  if (discount && discount > 0 && discount < 1 ){
    order['amount_paid'] = order['total_cost'] * (1 - discount);
  } else {
    order['amount_paid'] = order['total_cost'];
  }

  updateOrderTotalText(discount);
}

function updateOrderTotalText(discount) {
  const order_total_text = document.getElementById('total-price');

 if (discount && order['total_cost'] > 0 && discount > 0 && discount < 1) {
    order_total_text.innerHTML = `Total: <s>$${order['total_cost'].toLocaleString('en-US', { maximumFractionDigits: 2 })}</s> $${order['amount_paid'].toLocaleString('en-US', { maximumFractionDigits: 2 })}`;
  } else {
    order_total_text.textContent = `Total: $${order['amount_paid'].toLocaleString('en-US', { maximumFractionDigits: 2 })}`;
  }
}


function applyCoupon() {
  const couponResultText = document.querySelector('#coupon-result-text');
  const couponCode = document.getElementById('#coupon-code-input').value;
  
  // Add coupn code discount if valid, notify if otherwise
  if (couponCodes.hasOwnProperty(couponCode)) {
      // Update discount info
      order['discount'] = couponCodes[couponCode];
      order['amount_paid'] = order['total_cost'] * (1 - couponCodes[couponCode]);
      updateOrderTotalText(order['discount']);
      // Update cart discount text
      couponResultText.style.color = '#007bff';
      couponResultText.innerText = `Congrats you got ${Number(order['discount']*100)}% off!`;
  } else {
    couponResultText.innerText = 'Coupon not found :/';
  }
}


function closeCartModal() {
  const cartModal = document.querySelector('#cart-modal');
  cartModal.style.display = 'none';

  const couponResultText = document.querySelector('#coupon-result-text');
  
  if (order['discount'] === 0) {
    couponResultText.innerText = '';
  }
}
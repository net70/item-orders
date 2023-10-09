// Page landing
//  - re-render cart if cart > 0
// Cart Open: 
// - Update cart items and pricde AJAX on open cart
// Add Items:
// - Update cart rows UI, "cache"
// Remove Items: 
//  - Update cart rows UI, "cache"
//  - Update Price UI, "cache"



const order = {
  'user_id': undefined,
  'first_name': undefined,
  'last_name': undefined,
  'email': undefined,
  'items': [],
  'total_cost': 0,
  'amount_paid': 0,
  'discount': 1
};

const couponCodes = {
  'entery10': 0.1,
  'nice_15': 0.15,
  'super_20': 0.2,
  'vip_delight': 0.4
};

function submitEntryForm() {
  // Validate the form fields
  const firstName = document.getElementById("first_name").value;
  const lastName = document.getElementById("last_name").value;
  const email = document.getElementById("email").value;

  if (!firstName || !lastName || !email) {
      alert("All fields are mandatory. Please fill them out.");
      return;
  }

  order['first_name'] = firstName;
  order['last_name'] = lastName;
  order['email'] = email;

  // Assuming validation is successful, hide the prompt
  document.getElementById("prompt-modal").style.display = "none";
}

// Cart Management
class Node {
  constructor(data) {
    this.data = data;
    this.prev = null;
    this.next = null;
  }
}

class DoublyLinkedList {
  constructor() {
    this.head = null;
    this.tail = null;
  }

  add(data) {
    const newNode = new Node(data);
    if (!this.head) {
      this.head = newNode;
      this.tail = newNode;
    } else {
      newNode.prev = this.tail;
      this.tail.next = newNode;
      this.tail = newNode;
    }
    return newNode;
  }

  removeNode(node) {
    if (node) {
      // Update the next node's prev property
      if (node.next) {
          node.next.prev = node.prev;
      } else {
        // If it's the tail node, update the tail
        this.tail = node.prev;
      }

      // Update the previous node's next property
      if (node.prev) {
          node.prev.next = node.next;
      } else {
        // If it's the head node, update the head
        this.head = node.next;
      }

      // Remove the mapping from the nodeIndex object
      return node;
    }
  }
}

const cartList = new DoublyLinkedList();
let itemsIndex = {};
let numItemsInCart = 0;

function removeFromCart(itemId) {
  const itemData = itemsIndex[itemId].data;

  // Deduct ordered item from the total price
  updateOrderTotal(itemData['quantity'], itemData['price'], 'remove');

  const itemRow = document.getElementById(`cart-row-item-${itemId}`);
  if (itemRow) {
      itemRow.remove();
  }

  const cartIcon = document.getElementById('cart-counter');
  numItemsInCart -= 1;
  cartIcon.innerText = numItemsInCart;

  if (numItemsInCart === 0) {
    order['total_cost']  = 0;
    order['amount_paid'] = 0;
  }

  // Delete the item
  cartList.removeNode(itemsIndex[itemId]);
  itemsIndex[itemId] = null;
  delete itemsIndex[itemId];
  
  console.log(cartList);
  console.log(order['total_cost']);

  return;
}

function addToCart(itemId, itemName, price) {
  const quantityInput = Number(document.getElementById(`${itemId}-quantity`).value);
  const itemPrice = Number(price);

  if (itemsIndex.hasOwnProperty(itemId)) {
      itemsIndex[itemId].data['quantity'] += quantityInput;
  } else {
      itemsIndex[itemId] = cartList.add({
        'item_id': itemId,
        'item_name': itemName,
        'quantity': quantityInput,
        'price': itemPrice
      });

      const cartIcon = document.getElementById('cart-counter');
      numItemsInCart += 1;
      cartIcon.innerText = numItemsInCart;
  }

  _addItemRow(itemId, itemName, itemPrice, quantityInput);

  updateOrderTotal(quantityInput, itemPrice, 'add');

  console.log(cartList);
  console.log(order['total_cost']);
  console.log(order);
}


function _addItemRow(itemId, itemName, price, quantity) {
  // If adding to an item that already exists in the cart
  const existingItemRow =document.querySelector(`#cart-row-item-${itemId} #item-quantity`);
  if (existingItemRow) {
    existingItemRow.textContent = Number(existingItemRow.textContent) + quantity;
    return;
  }

  // Create a new <tr> element.
  const newRow = document.createElement("tr");
  newRow.setAttribute("id", `cart-row-item-${itemId}`);
  
  // Create a new <td> element for each variable and Remove item button.
  const itemNameTd = document.createElement("td");
  itemNameTd.setAttribute("class", "item_name");

  const priceTd = document.createElement("td");

  const quantityTd = document.createElement("td");
  quantityTd.setAttribute("id", "item-quantity");

  const removeItemButtonTd = document.createElement("td");
  const removeItemButton = document.createElement('button');
  removeItemButton.setAttribute("class", "item-remove-button");
  removeItemButton.setAttribute("onclick", "removeFromCart('" +  itemId + "')");
  removeItemButtonTd.appendChild(removeItemButton);
  
  // Set the text content of each <td> element to the value of the corresponding variable.
  itemNameTd.textContent = itemName;
  priceTd.textContent = `$${price}`;
  quantityTd.textContent = quantity;
  removeItemButton.textContent = "X";

  // Append the <td> elements to the <tr> element.
  newRow.appendChild(itemNameTd);
  newRow.appendChild(priceTd);
  newRow.appendChild(quantityTd);
  newRow.appendChild(removeItemButtonTd);
  
  // Insert the new row at the end of the table.
  const tableBody = document.querySelector(".cart-items tbody");
  //tableBody.insertRow(-1).appendChild(newRow);
  tableBody.appendChild(newRow);
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

function updateOrderTotalText(discount) {
  const order_total_text = document.getElementById('total-price');

 if (discount && order['total_cost'] > 0 && discount > 0 && discount < 1) {
    order_total_text.innerHTML = `Total: <s>$${order['total_cost'].toLocaleString('en-US', { maximumFractionDigits: 2 })}</s> $${order['amount_paid'].toLocaleString('en-US', { maximumFractionDigits: 2 })}`;
  } else {
    order_total_text.textContent = `Total: $${order['amount_paid'].toLocaleString('en-US', { maximumFractionDigits: 2 })}`;
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
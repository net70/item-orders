//import  DoublyLinkedList from './items-management.js';
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
  


let order = {
    'user_id': undefined,
    'first_name': undefined,
    'last_name': undefined,
    'email': undefined,
    'items': [],
    'original_price': 0,
    'total_cost': 0,
    'discount': 1
}

const cartList = new DoublyLinkedList()
let itemsIndex = {}


function removeFromCart(itemId) {
    const itemData = itemsIndex[itemId].data;
    
    // Delete the item
    cartList.removeNode(itemsIndex[itemId]);
    itemsIndex[itemId] = null;
    delete itemsIndex[itemId];

    // Deduct ordered item from the total price
    updateCartTotal(itemData['quantity'], itemData['price'], 'remove');

    const itemRow = document.getElementById(`${itemId}-cart-row`);
    if (itemRow) {
        itemRow.remove()
    }
}

function addToCart(itemId, itemName, price) {
    const quantityInput = Number(document.getElementById(`${itemId}-quantity`).value);

    if (itemsIndex.hasOwnProperty(itemId)) {
        itemsIndex[itemId].data['quantity'] += quantityInput
    } else {
        itemsIndex[itemId] = cartList.add({
            'item_id': itemId,
            'item_name': itemName,
            'quantity': quantityInput,
            'price': Number(price)
        });
    }

    updateOrderTotal(quantityInput, price, 'add');

    console.log(cartList);
    console.log(order['original_price']);
    console.log(order);
}


function updateOrderTotal(quantity, price, operation) {

    const order_total_text = document.getElementById('total-price')

    if (operation = 'add') {
        order['original_price'] +=  quantity * price
    }
    else {
        order['original_price'] -=  quantity * price
    }

    order['total_cost'] = order['original_price'] * order['discount']

    order_total_text.textContent =  `Total: $${order['total_cost']}`

}

function applyCoupon(couponCode) {
    if (couponCode = '') {
        return;
    }
}

function closeCartModal() {
    const cartModal = document.querySelector('#cart-modal');
    cartModal.style.display = 'none';
}
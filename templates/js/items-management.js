// AJAX
// // Get all of the visible cart item placeholders.
// const visibleCartItemPlaceholders = document.querySelectorAll('.cart-item-placeholder:visible');

// // Create a batch of cart item IDs.
// const cartItemIds = visibleCartItemPlaceholders.map(cartItemPlaceholder => cartItemPlaceholder.dataset.id);

// // Fetch the cart item data for the batch of cart item IDs.
// fetch(`/api/cart-items/batch/${cartItemIds.join(',')}`)
//   .then(response => response.json())
//   .then(cartItemData => {
//     // Populate the placeholder elements with the cart item data.
//     for (const cartItem of cartItemData) {
//       const cartItemPlaceholder = document.querySelector(`.cart-item-placeholder[data-id="${cartItem.id}"]`);

//       cartItemPlaceholder.innerHTML = `
//         <div class="cart-item">
//           <img src="${cartItem.image_url}" alt="${cartItem.name}">
//           <div class="cart-item-info">
//             <h3>${cartItem.name}</h3>
//             <p>${cartItem.description}</p>
//             <h4>${cartItem.price}</h4>
//           </div>
//         </div>
//       `;
//     }
//   });
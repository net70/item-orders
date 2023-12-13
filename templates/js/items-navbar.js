// load the cart
document.addEventListener('DOMContentLoaded', loadCart);

// JavaScript to handle scrolling and applying the fixed-navbar class
window.addEventListener('scroll', function() {
  var navbar = document.getElementById('navbar-wrapper');
  if (window.scrollY > 0) {
    navbar.classList.add('fixed-navbar');
  } else {
    navbar.classList.remove('fixed-navbar');
  }
});

// Load the cart from the localStorage
const itemsInCart = JSON.parse(localStorage.getItem('cart'));

// Update the cart counter
document.getElementById('cart-counter').innerText = itemsInCart.length;

function openCartModal(){
    const cartModal = document.querySelector('#cart-modal');
    cartModal.style.display = 'block';
}
///filter feature
function toggleFilter(){
    var filterDiv = document.getElementById("filterDiv");
    filterDiv.style.display = (filterDiv.style.display === "none") ? "block" : "none";}

  var baseUrl = "/listings"

  document.getElementById("locationFilterForm").addEventListener("submit", function(e) { e.preventDefault();
  var params = new URLSearchParams(window.location.search);
  var location = document.getElementById("locationInput").value;
  params.set("location", location);
  window.location.href = baseUrl + "?" + params.toString(); });

  document.getElementById("priceFilterForm").addEventListener("submit", function(e) { e.preventDefault();
  var params = new URLSearchParams(window.location.search);
  var minPrice = document.getElementById("minPriceInput").value;
  var maxPrice = document.getElementById("maxPriceInput").value;
  if (minPrice){
  params.set("minPrice", minPrice);
  }
  if (maxPrice){
  params.set("maxPrice", maxPrice);
  }
  alert(minPrice)
  window.location.href = baseUrl + "?" + params.toString(); });

  document.getElementById("typeFilterForm").addEventListener("submit", function(e) { e.preventDefault();
  var params = new URLSearchParams(window.location.search);
  var type = document.getElementById("typeInput").value;
  params.set("type", type);
  window.location.href = baseUrl + "?" + params.toString(); });

// Image slider
var slideIndex = 1;
showSlides(slideIndex);

function plusSlides(n) {
  showSlides(slideIndex += n);
}

function showSlides(n) {
  var i;
  var slides = document.getElementsByClassName("mySlides");

  if (n > slides.length) { slideIndex = 1 }
  if (n < 1) { slideIndex = slides.length }

  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }

  slides[slideIndex - 1].style.display = "block";
}

function toggleFilter(){
  var filterDiv = document.getElementById("filterDiv");
  filterDiv.style.display = (filterDiv.style.display === "none") ? "block" : "none";}

  var url = ""
  document.getElementById("locationFilterForm").addEventListener("submit", function(e) { e.preventDefault();
  var location = document.getElementById("locationInput").value;
  window.location.href = "/listings?location=" + encodeURIComponent(location); })

  document.getElementById("priceFilterForm").addEventListener("submit", function(e) { e.preventDefault();
  var minPrice = document.getElementById("minPriceInput").value;
  var maxPrice = document.getElementById("maxPriceInput").value;
  window.location.href = "/listings?minPrice=" + encodeURIComponent(minPrice) + "&maxPrice=" + encodeURIComponent(maxPrice) ; })

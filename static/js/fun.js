document.addEventListener("DOMContentLoaded", function() {
  const squares = document.querySelectorAll(".square");

  squares.forEach(square => {
    // On hover, scale the square (handled via CSS transition)
    square.addEventListener("mouseover", () => {
      square.style.transform = "scale(1.05)";
    });

    square.addEventListener("mouseout", () => {
      square.style.transform = "scale(1)";
    });
  });

  // Add click events for specific squares to navigate to different pages
  document.getElementById("square3").addEventListener("click", function() {
    window.location.href = "/premade"; // Redirect to Premade Parlays page
  });

  document.getElementById("square4").addEventListener("click", function() {
    window.location.href = "/build-your-own"; // Redirect to Build Your Own page
  });

  document.getElementById("square5").addEventListener("click", function() {
    window.location.href = "/personal-stats"; // Redirect to Personal Stats page
  });
  
  document.getElementById("square6").addEventListener("click", function() {
    window.location.href = "/free-75"; // Redirect to Free 75 page
  });
});

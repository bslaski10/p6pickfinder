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
  });
  
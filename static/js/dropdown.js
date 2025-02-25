document.addEventListener("DOMContentLoaded", function() {
    const dropbtn = document.querySelector(".dropbtn");
    const dropdownContent = document.querySelector(".dropdown-content");

    dropbtn.addEventListener("click", function(event) {
        dropdownContent.style.display = dropdownContent.style.display === "block" ? "none" : "block";
        event.stopPropagation();
    });

    document.addEventListener("click", function() {
        dropdownContent.style.display = "none";
    });
});

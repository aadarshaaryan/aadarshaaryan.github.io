document.getElementById("mobile-toggle").addEventListener("click", function (e) {
    e.preventDefault();
    const menu = document.getElementById("mobile-menu");
    menu.style.display = (menu.style.display === "flex") ? "none" : "flex";
});

let mobileToggle = document.getElementById("mobile-toggle");
let mobileMenu = document.getElementById("mobile-menu");
let sidebarClose = document.getElementById("sidebar-close"); 

// Toggle the sidebar when clicking the hamburger icon
if (mobileToggle) { 
    mobileToggle.addEventListener("click", function (e) { 
        e.preventDefault(); 
        if (mobileMenu) { 
            mobileMenu.classList.toggle("active"); 
        }
    });
}

// Close the sidebar when clicking the "X" button
if (sidebarClose) {
    sidebarClose.addEventListener("click", function () {
        if (mobileMenu) {
            mobileMenu.classList.remove("active");
        }
    });
}

document.addEventListener("click", function (e) {
    if (mobileMenu && mobileToggle) {
        let isClickInsideMenu = mobileMenu.contains(e.target);
        let isClickInsideToggle = mobileToggle.contains(e.target);

        if (!isClickInsideMenu && !isClickInsideToggle) {
            mobileMenu.classList.remove("active");
        }
    }
});

var swiped = false;
var last_main_nav = document.querySelector(".bottom-nav-items:last-child");
var mobile_nav = document.querySelector(".bottom-nav");
var hiddenLinks = document.querySelectorAll(".bottom-nav-items.hidden");

function swipe_left() {
    if (!last_main_nav || !mobile_nav) {
        return;
    }

    last_main_nav.addEventListener("click", function () {
        
        // Toggle the rotation class smoothly
        last_main_nav.classList.toggle("rotated");

        // Toggle the visibility of the hidden items
        hiddenLinks.forEach(function (link) {
            link.classList.toggle("hidden-item");
        });

        // Handle the container shrinking logic
        if (!swiped) {
            mobile_nav.classList.add("is-shrunk");
            swiped = true;
        } else {
            mobile_nav.classList.remove("is-shrunk");
            swiped = false;
        }
    });
}

swipe_left();
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

// Close mobile menu if clicked outside
document.addEventListener("click", function (e) {
    if (mobileMenu && mobileToggle) {
        let isClickInsideMenu = mobileMenu.contains(e.target);
        let isClickInsideToggle = mobileToggle.contains(e.target);

        if (!isClickInsideMenu && !isClickInsideToggle) {
            mobileMenu.classList.remove("active");
        }
    }
});

// 1. Triggers loader during standard page navigation leaves
window.addEventListener('beforeunload', function () {
    document.getElementById('global-page-loader').classList.add('loader-active');
});

// 2. Clear loader if the page is pulled out of the Back-Forward Cache (bfcache)
window.addEventListener('pageshow', function (event) {
    if (event.persisted) {
        document.getElementById('global-page-loader').classList.remove('loader-active');
    }
});

// 3. Triggers loader during form processing pipelines
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function () {
        document.getElementById('global-page-loader').classList.add('loader-active');
    });
});

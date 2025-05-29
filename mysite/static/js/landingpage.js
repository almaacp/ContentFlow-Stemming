function toggleDropdown() {
    const dropdown = document.querySelector('.dropdown');
    dropdown.classList.toggle('active'); // Toggle the active class
}

// Optional: Close the dropdown when clicking outside of it
window.onclick = function(event) {
    if (!event.target.matches('.dropdown button')) {
        const dropdowns = document.querySelectorAll('.dropdown');
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove('active');
        });
    }
}
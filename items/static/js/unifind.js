/* ==========================================================================
   UniFind — shared behaviour
   Every handler checks the element exists first, so one file safely
   covers every page (only the matching elements on each page react).
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function () {

    /* Sidebar drawer toggle (mobile navbar hamburger) */
    var sidebarToggle = document.getElementById('sidebarToggle');
    var sidebar = document.getElementById('sidebar');
    var backdrop = document.getElementById('sidebarBackdrop');

    if (sidebarToggle && sidebar && backdrop) {

        function closeSidebar() {
            sidebar.classList.remove('open');
            backdrop.classList.remove('visible');
        }

        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('open');
            backdrop.classList.toggle('visible');
        });

        backdrop.addEventListener('click', closeSidebar);

        window.addEventListener('resize', function () {
            if (window.innerWidth > 900) {
                closeSidebar();
            }
        });
    }

    /* Image preview on the add-item form */
    var imageInput = document.getElementById('id_image');
    var imagePreview = document.getElementById('image-preview');

    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', function (event) {
            var file = event.target.files[0];

            if (!file) {
                return;
            }

            var reader = new FileReader();

            reader.onload = function (e) {
                imagePreview.src = e.target.result;
                imagePreview.style.display = 'block';
            };

            reader.readAsDataURL(file);
        });
    }

    /* Lost / Found status filter on the home board */
    var statusFilter = document.getElementById('statusFilter');

    if (statusFilter) {
        statusFilter.addEventListener('change', function () {
            var selectedFilter = this.value;
            var cards = document.querySelectorAll('.ticket');

            cards.forEach(function (card) {
                var cardStatus = card.getAttribute('data-status');

                if (selectedFilter === 'all' || cardStatus === selectedFilter) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }

});

/* Confirmation prompt for the "Claim Item" link */
function confirmClaim() {
    return confirm('Are you sure you want to claim this item?');
}

document.addEventListener('DOMContentLoaded', function() {
    const today = new Date();
    const dateInput = document.querySelector('input[type="date"]');
    if (dateInput) {
        dateInput.valueAsDate = today;
    }

});
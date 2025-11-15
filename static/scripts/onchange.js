function formatDateToBR(value) {
    if (!value) return '';
    let [year, month, day] = value.split('-');
    if (!year || !month || !day) return '';

    // Garante que o ano tenha no máximo 4 dígitos
    year = year.slice(0, 4);

    return `${day}/${month}/${year}`;
}

function handleDateChange() {
    const input = document.getElementById('date');
    if (!input) return;

    // Conserta o valor do input também (YYYY-MM-DD)
    let [year, month, day] = (input.value || '').split('-');
    if (year && month && day) {
        year = year.slice(0, 4); // força 4 dígitos
        input.value = `${year}-${month}-${day}`;
    }

    const formatted = formatDateToBR(input.value);
    const target = document.getElementById('dateFormatted');
    if (target) {
        target.textContent = formatted;
    }
}

document.addEventListener('DOMContentLoaded', function () {
    handleDateChange();
});

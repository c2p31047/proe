const searchBox = document.getElementById('searchBox');
const adminTable = document.getElementById('adminTable');

searchBox.addEventListener('input', function() {
    const filter = searchBox.value.toLowerCase();
    const rows = adminTable.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
    for (let i = 0; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        let rowContainsFilter = false;
        for (let j = 0; j < cells.length - 1; j++) {
            if (cells[j].textContent.toLowerCase().includes(filter)) {
                rowContainsFilter = true;
                break;
            }
        }
        rows[i].style.display = rowContainsFilter ? '' : 'none';
    }
});
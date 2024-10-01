document.addEventListener('DOMContentLoaded', function() {
    const map = L.map('map').setView([35.3331, 139.4042], 14);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    const sheltersData = JSON.parse(document.getElementById('sheltersData').textContent);

    sheltersData.forEach(shelter => {
        L.marker([shelter.latitude, shelter.longitude])
            .addTo(map)
            .bindPopup(`
                <strong>${shelter.name}</strong><br>
                想定収容人数: ${shelter.capacity || '不明'}人<br>
                住所: ${shelter.address}<br>
                <a href="/shelter/${shelter.id}">詳細を見る</a>
            `);
    });
});
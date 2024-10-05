document.addEventListener('DOMContentLoaded', function() {
    const map = L.map('map').setView([35.3331, 139.4042], 14);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
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

    function searchDatabase(query) {
        // sheltersDataから一致するものを検索
        return sheltersData.filter(shelter => shelter.name.includes(query) || shelter.address.includes(query));
    }

    function performSearch(query) {
        const results = searchDatabase(query);
        if (results.length > 0) {
            // データベースから一致するものを表示
            results.forEach(shelter => {
                // マーカーの位置を表示
                map.setView([shelter.latitude, shelter.longitude], 14);
            });
        } else {
            // 一致するものがない場合、GEOSearchで検索
            if (typeof query === 'string' && query.trim() !== '') {
                osmGeocoder.geocode(query);
            } else {
                console.error('Invalid query for geocoding');
            }
        }
    }

    var osmGeocoder = new L.Control.OSMGeocoder({
        placeholder: '場所を検索する',
        text: '検索',
        bounds: L.latLngBounds(
            [35.3000, 139.3500],
            [35.3667, 139.4500]
        )
    });

    map.addControl(osmGeocoder);

    // 検索ボタンのクリックイベントを追加
    document.getElementById('searchButton').addEventListener('click', function() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            const query = searchInput.value;
            performSearch(query);
        } else {
            console.error('Search input element not found');
        }
    });

    /*osmGeocoder.on('click', function(e) {
        const query = e.target.value;
        performSearch(query);
    });*/
});

document.addEventListener('DOMContentLoaded', function() {
    // 茅ヶ崎市の中心座標
    var chigasakiCoords = [35.33384389, 139.40362191];

    var map = L.map('map').setView(chigasakiCoords, 15);

    // OpenStreetMapタイルレイヤーの追加
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // 避難所データを取得
    var sheltersData = JSON.parse(document.getElementById('sheltersData').textContent);

    // 各避難所の位置にマーカーを追加
    sheltersData.forEach(function(shelter) {
        var marker = L.marker([shelter.latitude, shelter.longitude]).addTo(map);
        marker.bindPopup(shelter.name); // 避難所名をポップアップで表示

        // 避難所一覧にアイテムを追加
        var listItem = document.createElement('li');
        listItem.textContent = shelter.name;
        listItem.addEventListener('click', function() {
            map.setView([shelter.latitude, shelter.longitude], 18); // クリック時にズーム
            marker.openPopup(); // ポップアップを開く
        });
        document.getElementById('shelter-items').appendChild(listItem);
    });

    // サイドパネルの折りたたみ機能
    var panel = document.getElementById('shelter-panel');
    var toggleButton = document.getElementById('toggle-button');

    toggleButton.addEventListener('click', function() {
        panel.classList.toggle('collapsed'); // パネルの折りたたみを切り替える
        if (panel.classList.contains('collapsed')) {
            toggleButton.textContent = '≫'; // パネルが折りたたまれたときのボタンテキスト
        } else {
            toggleButton.textContent = '≪'; // パネルが表示されているときのボタンテキスト
        }
    });
});

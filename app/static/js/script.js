//メッセージ系
document.addEventListener('DOMContentLoaded', () => {
    const errorContainer = document.querySelector('.error-container');
    if (errorContainer) {
        const labels = document.querySelectorAll('label[data-error-message]');
        labels.forEach(label => {
            const customMessage = label.getAttribute('data-error-message');
            if (customMessage) {
                const errorElement = errorContainer.querySelector('.error');
                if (errorElement) {
                    const paragraphs = errorElement.querySelectorAll('p');
                    paragraphs.forEach(p => {
                        p.textContent = customMessage;
                    });
                }
            }
        });
    }
});

//ハンバーガーメニュー系
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');

    menuToggle.addEventListener('click', function() {
        menuToggle.classList.toggle('active'); // アイコンのアニメーション
        navMenu.classList.toggle('active'); // メニューの表示/非表示
    });
});

//郵便番号から住所検索
$(document).ready(function() {
    $('#postal_code').on('blur', function() {
        var postalCode = $(this).val();
        if (postalCode.length === 7) {
            $.getJSON(`https://api.zipaddress.net/?zipcode=${postalCode}`, function(data) {
                if (data.code === 200) {
                    $('#address').val(data.data.fullAddress);
                } else {
                    alert('住所が取得できませんでした。');
                }
            }).fail(function() {
                alert('郵便番号が無効です。');
            });
        }
    });
});
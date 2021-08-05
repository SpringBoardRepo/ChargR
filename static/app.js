const image = document.querySelector('.map-img');
const lat = document.querySelector('.map-img').getAttribute('latitude')
const lng = document.querySelector('.map-img').getAttribute('longitude')

image.addEventListener('click', function () {
    window.open(`https://map.openchargemap.io/?mode=embedded&latitude=${lat}&longitude=${lng}`);
});
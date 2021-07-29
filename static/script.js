let dropdown = document.getElementById('custom-dropdown');
dropdown.addEventListener('click', function(event) {
    event.stopPropagation();
    dropdown.classList.toggle('is-active');
});

let aButton = document.getElementById('show-button');
aButton.addEventListener('click', function(event) {
    event.stopPropagation();
    let aDiv = document.getElementById('show-div');
    aDiv.classList.toggle('is-hidden')
});
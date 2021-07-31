let dropdown = document.getElementById('custom-dropdown');
dropdown.addEventListener('click', function(event) {
    event.stopPropagation();
    dropdown.classList.toggle('is-active');
});

let aButton = document.getElementById('show-button');
aButton.addEventListener('click', function(event) {
    event.stopPropagation();
    let showDiv = document.getElementById('show-div');
    showDiv.classList.toggle('is-hidden')
    if (showDiv.classList.contains('is-hidden')) {
        window.scrollTo(0, 0);
    } else {
        showDiv.scrollIntoView()
    };
});
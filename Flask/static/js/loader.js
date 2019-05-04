let loader = document.getElementById("loader");

toggle_loader_off();
function toggle_loader_on() {
    loader.style.display = "block";
}

function toggle_loader_off() {
    loader.style.display = "none"
}
/*
document.addEventListener("DOMContentLoaded", function(event) {
    toggle_loader_off()
});*/

document.getElementsByTagName("body")[0].onload = function() {
    toggle_loader_off()
};
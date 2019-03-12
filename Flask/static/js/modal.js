var modal = document.getElementsByClassName('modal');
var btn = document.getElementsByClassName('modal_button');
var span = document.getElementsByClassName('close');

console.log(modal);

btn[0].onclick = function () {
    modal[0].style.display = "block";    
};

span[0].onclick = function () {
    modal[0].style.display = "none";
};

btn[1].onclick = function () {
    modal[1].style.display = "block";
};

span[1].onclick = function () {
    modal[1].style.display = "none";
};

window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
} 
let modal = document.getElementsByClassName('modal');
let modal_button = document.getElementsByClassName('modal_button');
let span = document.getElementsByClassName('close');
let body = document.querySelector('body');

// Adds event to all present modal buttons
for (let btn = 0; btn < modal_button.length ; btn++) {
    if (modal_button[btn] != null) {
        modal_button[btn].onclick = function () {
            modal[btn].style.display = "block";
            body.style.overflow = "hidden";
        };
    }
    if (span[btn] != null) {
        span[btn].onclick = function () {
            modal[btn].style.display = "none";
            body.style.overflow = "auto";
        };
    }
}

/**
 * Changes mode in new account modal
 */
function change_account_mode() {
    let type = document.getElementById("account_type").value;
    if (type === "regular") {
        document.getElementById("foreign").style.display = "none";
    }
    if (type === "irregular") {
        document.getElementById("foreign").style.display = "grid";
    }
}
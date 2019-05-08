let counter = 1; //Counter to represent amount of made lines

init();

/**
 * Initializes the purchase and sale pages by adding a purchase or sale line.
 */
function init() {
    if (document.getElementById("purchase-form")) {
        add_purchase_line();
    }
    if (document.getElementById("sale-form")) {
        add_product_line();
    }
}

/**
 * Adds an element to the document.
 * @param parentId The id of parent element.
 * @param elementClass The class of the new element.
 * @param elementTag The tag of the new element.
 * @param elementId The id of the new element.
 * @param html The html to be filled in new element.
 */
function addElement(parentId, elementClass, elementTag, elementId, html) {
    // Adds an element to the document
    let p = document.getElementById(parentId);
    let newElement = document.createElement(elementTag);
    newElement.setAttribute('class', elementClass);
    newElement.setAttribute('id', elementId);
    newElement.innerHTML = html;
    p.appendChild(newElement);
    counter++;
}

/**
 * Removes an element in document.
 * @param elementId The id of element to be removed.
 */
function removeElement(elementId) {
    let element = document.getElementById(elementId);
    if (element != null) {
        element.parentNode.removeChild(element);
    }
}
let mdblock = document.getElementById("maturity_date-block");
let mdblock_filler = document.getElementById("maturity_date-block-filler");
let paid = document.getElementById("pf-paid");
let payment = document.getElementById("pf-payment");
let supplier = document.getElementById("supplier");
let supplier_button = document.getElementById("supplier-button");
let amount = document.getElementById("amount");

let counter = 1; //Counter to represent amount of made lines

init();

function init() {
    if (document.getElementById("purchase-form")) {
        add_purchase_line();
    }
    if (document.getElementById("sale-form")) {
        add_product_line();
    }
}


// PURCHASE FORM
// -- Mode Selection

/**
 * Changes the mode to supplier mode.
 */
function mode_supplier() {
    mdblock.style.display = "grid";
    paid.style.display = "grid";
    payment.style.display = "none";
    supplier.disabled = false;
    supplier_button.disabled = false;
}

/**
 * Changes the mode to cash mode.
 */
function mode_cash() {
    mdblock.style.display = "none";
    paid.style.display = "none";
    payment.style.display = "grid";
    supplier.disabled = true;
    supplier_button.disabled = true;
}


// -- Line selection

/**
 * Adds a new line to purchase form.
 */
function add_purchase_line() {
    let purchase_line = createHTML("purchase_line");
    let parent = "pf-lines";
    let element = "div";
    let element_id = "pf-line-"+counter;
    addElement(parent, "pf-line", element, element_id, purchase_line);
}

/**
 * Removes a line in purchase form.
 * @param id The id of line to be removed.
 */
function remove_purchase_line(id) {
    let pf_lines = document.getElementById("pf-lines");
    if (pf_lines.children.length > 1){
        removeElement(id);
    } else {
        // TODO - Flash if only one element is left
        console.log("Cant remove line");
    }
}

/**
 * Clears the purchase form for input and deletes lines.
 */
function clear_purchase_form() {
    document.getElementById("purchase-form").reset();
    for (let i = 1; i < counter; i++) {
        let id = "pf-line-"+i;
        remove_purchase_line(id);
    }
}

let purchaseForm = document.getElementById("purchase-form");

/**
 * Changes the net value in a line.
 * Used when gross amount is changed.
 */
function change_net(){
    // TODO - Change value of gross field when net field is changed.
    let gross_total = 0;
    let net_total = 0;
    for (let i = 1; i < counter; i++) {
        let gross_id = "gross_amount-" + i;
        let net_id = "net_amount-" + i;
        let gross_pointer = document.getElementById(gross_id);
        let net_pointer = document.getElementById(net_id);
        if (gross_pointer != null){
            let gross_amount = Number(gross_pointer.value);
            let net_amount = gross_amount/(1.25);
            net_pointer.value = net_amount;
            gross_total += gross_amount;
            net_total += net_amount;
        }
    }
    let vat_total = gross_total-net_total;
    change_total(gross_total, vat_total, net_total);
}


/**
 * Changes the total field.
 * @param gross_total The gross total.
 * @param vat_total The vat total.
 * @param net_total The net total.
 */
function change_total(gross_total, vat_total, net_total) {
    let total = document.getElementById("pf-total");
    let amount = document.getElementById("amount");
    total.innerHTML = "Totalbeløp: " + net_total.toFixed(2) + " + mva: " +
        vat_total.toFixed(2) +" = " +  gross_total.toFixed(2);
    amount.value = gross_total;
}


// SALE FORM

function update_maturity_date() {
    let days = document.getElementById("days_to_maturity").value;
    let time = new Date();
    time.setDate(time.getDate()+Number(days));
    let day = time.getDate();
    let month = time.getMonth() + 1;
    let year = time.getFullYear();
    document.getElementById("maturity-text").innerHTML = "Forfallsdato: " + day +"." + month + "." + year;
}

// -- Line selection
/**
 * Adds a new product line to sale form.
 */
function add_product_line() {
    let id = "sf-line-" + counter;
    let product_line = createHTML("product_line");
    addElement("sf-lines", "sf-line", "div", id, product_line);
    update_sale_lines();
}

/**
 * Adds a new freetext line to sale form.
 */
function add_freetext_line() {
    let id = "sf-line-" + counter;
    let freetext_line = createHTML("freetext_line");
    addElement("sf-lines", "sf-line", "div", id, freetext_line);
    update_sale_lines();
}


/**
 * Removes a line in purchase form.
 * @param id The id of line to be removed.
 */
function remove_sale_line(id) {
    let sf_lines = document.getElementById("sf-lines");
    if (sf_lines.children.length > 1){
        removeElement(id);
    } else {
        // TODO - Flash if only one element is left
        console.log("Cant remove line");
    }
    update_sale_lines();
}

/**
 * Clears the purchase form for input and deletes lines.
 */
function clear_sale_form() {
    document.getElementById("sale-form").reset();
    for (let i = 1; i < counter; i++) {
        let id = "sf-line-"+i;
        remove_sale_line(id);
    }
    update_sale_lines();
}

function update_sale_lines() {
    change_sale_line_total();
    change_sale_total();
}

function change_sale_line_total() {
    // TODO - Calculate vat
    for (let i = 1; i < counter; i++){
        let price_pointer = document.getElementById("price-"+i);
        let discount_pointer = document.getElementById("discount-"+i);
        let amount_pointer = document.getElementById("amount-"+i);
        if (price_pointer != null) {
            let price = price_pointer.value;
            let discount = discount_pointer.value;
            let amount = amount_pointer.value;
            let total = amount*price;
            if (discount > 0) {total = total*(1-(discount/100))}
            document.getElementById("sf-line-total-"+i).innerHTML = total.toFixed(2);
        }
    }
}

function change_sale_total() {
    // TODO - Add vat calculation
    let total = document.getElementById("sf-total");
    let gross_amount = 0;
    let net_amount = 0;
    let vat_amount = 0;
    for (let i = 1; i < counter; i++){
        let total_pointer = document.getElementById("sf-line-total-"+i);
        if (total_pointer != null) {
            gross_amount += Number(total_pointer.innerHTML)
        }
    }
    total.innerHTML = gross_amount.toFixed(2) + " " + "(0.00 inkl. mva)"
}



// GENERAL

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

/**
 * Creates HTML for document
 * @param type The HTML type
 * @returns {string} The HTML for specific type.
 */
function createHTML(type) {
    if (type === "purchase_line") {
        return `
            <div class="pf-line-input">
                <h4 class="pf-header-hidden"> Tekst</h4>
                <input id="text-${counter}" name="text-${counter}" type="text">
            </div>
            <div class="pf-line-input">
                <h4 class="pf-header-hidden">Kostnadskonto</h4>
                <select id="billing_account-${counter}" name="billing_account-${counter}"></select>
            </div>
            <div class="pf-line-input">
                <h4 class="pf-header-hidden">Bruttobeløp</h4>
                <input id="gross_amount-${counter}" name="gross_amount-${counter}" type="number" onchange="change_net()">
            </div>
            <div class="pf-line-input">
                <h4 class="pf-header-hidden">Mva</h4>
                <select id="vat-${counter}" name="vat-${counter}"></select>
            </div>
            <div class="pf-line-input">
                <h4 class="pf-header-hidden">Nettobeløp</h4>
                <input id="net_amount-${counter}" name="net_amount-${counter}" type="number" disabled>
            </div>
            <div class="pf-line-input">
                <input class="pf-button" id="pf-button-${counter}" type="button" value="Slett linje" onclick="remove_purchase_line(this.parentNode.parentNode.id)">
            </div>
            `;
    }
    else if (type === "product_line") {
        return `
            <div class="description-column">
                <div class="sf-line-input">
                    <select id="product-${counter}" name="product-${counter}"></select>
                </div>
                <div class="sf-line-input">
                    <h4 class="sf-header-hidden">Kommentar</h4>
                    <input id="sale_comment-${counter}" name="sale_comment-${counter}" type="text" placeholder="Kommentar (ikke påkrevd)">
                </div>
            </div>
            <div class="sf-line-input line-split">
                <h4 class="sf-header-hidden">Pris</h4>
                <input id="price-${counter}" name="price-${counter}" type="number" value="0.00" onchange="update_sale_lines()">
            </div>
            <div class="sf-line-input line-split">
                <h4 class="sf-header-hidden">Rabatt</h4>
                <input id="discount-${counter}" name="discount-${counter}" type="number" value="0" onchange="update_sale_lines()">
            </div>
            <div class="sf-line-input line-split">
                <h4 class="sf-header-hidden">Antall</h4>
                <input id="amount-${counter}" name="amount-${counter}" type="number" value="1" onchange="update_sale_lines()">
            </div>
            <div class="sf-line-input line-split">
                <h4 class="sf-header-hidden">Mva</h4>
                <select id="sale_vat-${counter}" name="sale_vat-${counter}" onchange="update_sale_lines()" disabled></select>
            </div>
            <div class="sf-line-input sf-line-button">
                <p class="sf-line-total" id="sf-line-total-${counter}">0.00</p>
                <input class="sf-button" id="sf-button-${counter}" type="button" Value="Slett linje" onclick="remove_sale_line(this.parentNode.parentNode.id)">
            </div>
            `;
    }
    else if (type === "freetext_line") {
        return `
            <div class="description-column">
                <div class="sf-line-input">
                    <h4 class="sf-header-hidden">Tekst</h4>
                    <input id="description" name="description" type="text">
                </div>
                <ul class="sf-line-input" id="sale-type">
                    <li>
                        <input name="sale_type-${counter}" type="radio" value="1" checked="checked">
                        <label for="sale_type-0">Vare (for videresalg)</label>
                    </li>
                    <li>
                        <input name="sale_type-${counter}" type="radio" value="2">
                        <label for="sale_type-1">Vare (egenprodusert)</label>
                    </li>
                    <li>
                        <input name="sale_type-${counter}" type="radio" value="3">
                        <label for="sale_type-2">Tjeneste</label>
                    </li>
                    <li>
                        <input name="sale_type-${counter}" type="radio" value="4">
                        <label for="sale_type-3">Annet</label>
                    </li>
                </ul>
                <div class="sf-line-input">
                    <h4 class="sf-header-hidden">Kommentar</h4>
                    <input id="sale_comment-${counter}" name="sale_comment-1" type="text">
                </div>
            </div>
            <div class="sf-line-input line-split">
                <h4 class="sf-header-hidden">Pris</h4>
                <input id="price-${counter}" name="price-${counter}" type="number" value="0.00" onchange="update_sale_lines()">
            </div>
            <div class="sf-line-input line-split">
                <h4 class="sf-header-hidden">Rabatt</h4>
                <input id="discount-${counter}" name="discount-${counter}" type="number" value="0" onchange="update_sale_lines()">
            </div>
            <div class="sf-line-input line-split">
                <h4 class="sf-header-hidden">Antall</h4>
                <input id="amount-${counter}" name="amount-${counter}" type="number" value="1" onchange="update_sale_lines()">
            </div>
            <div class="sf-line-input line-split">
                <h4 class="sf-header-hidden">Mva</h4>
                <select id="sale_vat-${counter}" name="sale_vat-${counter}" onchange="update_sale_lines()"></select>
            </div>
            <div class="sf-line-input sf-line-button">
                <p class="sf-line-total" id="sf-line-total-${counter}">0.00</p>
                <input class="sf-button" id="sf-button-${counter}" type="button" Value="Slett linje" onclick="remove_sale_line(this.parentNode.parentNode.id)">
            </div>
            `;
    }
}
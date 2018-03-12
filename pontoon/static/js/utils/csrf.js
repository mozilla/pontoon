

export class PontoonCSRF {

    get value () {
        return document.querySelector('input[name=csrfmiddlewaretoken]').value;
    }
}

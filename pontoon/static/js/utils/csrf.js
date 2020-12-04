export const getCSRFToken = () => {
    return document.querySelector('input[name=csrfmiddlewaretoken]').value;
};

function getReplacement(title, replacement) {
    return '<mark class="placeable" title="' + title + '">' + replacement + '</mark>';
}

function replaceMarkup(string, regex, title, replacement) {
    replacement = replacement || '$&';
    return string.replace(regex, getReplacement(title, replacement));
}

function safeRenderString(string) {
    return $('<div/>').text(string).html();
}

export function markAll(string) {
    string = safeRenderString(string);

    // Test of values
    string = replaceMarkup(string, / /gi, 'Any space');
    return string;
}

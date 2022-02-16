export class Strip {
    /**
     * This provides a utility for stripping chars from beginning or end
     * of strings.
     *
     * By default it will strip whitespace - spaces,
     */

    strip(str, char) {
        return this.rstrip(this.lstrip(str, char), char);
    }

    lstrip(str, char) {
        return str.replace(new RegExp('^' + (char || '\\s') + '+'), '');
    }

    rstrip(str, char) {
        const match = new RegExp('^[^' + (char || '\\s') + ']');
        for (var i = str.length - 1; i >= 0; i--) {
            if (match.test(str.charAt(i))) {
                return str.substring(0, i + 1);
            }
        }
    }
}

export const strip = new Strip();

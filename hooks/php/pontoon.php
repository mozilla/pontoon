<?php

/**
 * Wrapper for gettext(), returns Pontoon-wrapped strings to
 * be handled by the Pontoon client component
 */
function _w($original) {
    return Pontoon::wrap($original);
}

/**
 * Main hook component
 */
class Pontoon
{
    /**
     * Marks strings for localization with Pontoon comments
     */
    static function wrap($original) {
        if (!function_exists('gettext')) return sprintf('<!--l10n-->%1$s', $original);
        return sprintf('<!--l10n-->%1$s', gettext($original));
    }

    /**
     * Inject javascript to solve iframe cross-domain policy problem
     */
    static function header() {
        echo '<script src="https://pontoon.mozilla.org/pontoon.js"></script>'."\n";
    }
}

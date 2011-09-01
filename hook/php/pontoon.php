<?php
/* ***** BEGIN LICENSE BLOCK *****
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1
 *
 * The contents of this file are subject to the Mozilla Public License Version
 * 1.1 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the License is distributed on an "AS IS" basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
 * for the specific language governing rights and limitations under the
 * License.
 *
 * The Original Code is Pontoon.
 *
 * The Initial Developer of the Original Code is
 * The Mozilla Foundation.
 * Portions created by the Initial Developer are Copyright (C) 2009
 * the Initial Developer. All Rights Reserved.
 *
 * Contributor(s):
 *   Frederic Wenzel <fwenzel@mozilla.com> (Original Author)
 *
 * Alternatively, the contents of this file may be used under the terms of
 * either the GNU General Public License Version 2 or later (the "GPL"), or
 * the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
 * in which case the provisions of the GPL or the LGPL are applicable instead
 * of those above. If you wish to allow use of your version of this file only
 * under the terms of either the GPL or the LGPL, and not to allow others to
 * use your version of this file under the terms of the MPL, indicate your
 * decision by deleting the provisions above and replace them with the notice
 * and other provisions required by the GPL or the LGPL. If you do not delete
 * the provisions above, a recipient may use your version of this file under
 * the terms of any one of the MPL, the GPL or the LGPL.
 *
 * ***** END LICENSE BLOCK ***** */

/**
 * Wrapper for gettext(), returns Pontoon-wrapped strings to
 * be handled by the Pontoon client component
 */
function _w($original) {
    if (!Pontoon::has_gettext()) return $original;

    return Pontoon::wrap($original);
}

/**
 * Wrapper for ngettext()
 * FIXME: This probably does not work yet
 */
function n_w($str1, $str2, $ct) {
    if (!Pontoon::has_gettext()) return $str1;

    $translated = ngettext($str1, $str2, $ct);
    return Pontoon::wrap($translated, $str1);
}

/**
 * Main hook component
 */
class Pontoon
{
    /**
     * is gettext installed?
     */
    static function has_gettext() {
        return function_exists('gettext');
    }

    /**
     * marks strings for localization with Pontoon comments
     */
    static function wrap($original) {
        return sprintf('<!--l10n-->%1$s', $original);
    }

    /**
     * prints out header tags for the target app's template header, telling
     * the client that this is a Pontoon enhanced page
     */
    static function header_tags() {
        if (self::has_gettext()) echo '<meta name="Pontoon" content="Test Pilot" ip="http://0.0.0.0:8000/push/"/>'."\n";
    }
}

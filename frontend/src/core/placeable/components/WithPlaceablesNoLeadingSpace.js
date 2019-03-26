/* @flow */

import './WithPlaceables.css';

import createMarker from 'lib/react-content-marker';

import { rules } from './WithPlaceables';
import leadingSpace from '../parsers/leadingSpace';


function getRulesWithoutLeadingSpace(rules: Array<Object>) {
    let newRules = [ ...rules ];
    newRules.splice(newRules.indexOf(leadingSpace), 1);
    return newRules;
}


/**
 * Component that marks placeables in a string. Same as WithPlaceables but
 * without the leadingSpace parser.
 *
 * The leadingSpace parser checks for spaces at the beginning of a line.
 * If the input was previously split, then that parser will generate a lot of
 * false positive (for example, if something else was marked just before a
 * space, it thus becomes a space the beginning of a line). We thus want to
 * have a special Placeables component without that parser, for use in
 * combination with other parsing tools (like diff).
 */
const WithPlaceablesNoLeadingSpace = createMarker(getRulesWithoutLeadingSpace(rules));


export default WithPlaceablesNoLeadingSpace;

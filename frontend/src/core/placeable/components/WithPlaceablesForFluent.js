/* @flow */

import createMarker from 'react-content-marker';

import './WithPlaceables.css';

import { rules } from './WithPlaceables';
import fluentFunction from '../parsers/fluentFunction';
import fluentParametrizedTerm from '../parsers/fluentParametrizedTerm';
import fluentString from '../parsers/fluentString';
import fluentTerm from '../parsers/fluentTerm';
import multipleSpaces from '../parsers/multipleSpaces';

export function getRulesWithFluent(
    rules: Array<Object>,
): Array<
    | any
    | {| matchIndex: number, rule: any, tag: (x: string) => any |}
    | {| rule: any, tag: (x: string) => any |},
> {
    const newRules = [...rules];

    // Insert after the last space-related rule.
    let insertAfter = newRules.indexOf(multipleSpaces);
    newRules.splice(insertAfter, 0, fluentFunction);
    newRules.splice(insertAfter++, 0, fluentString);
    newRules.splice(insertAfter++, 0, fluentParametrizedTerm);
    newRules.splice(insertAfter++, 0, fluentTerm);

    return newRules;
}

/**
 * Component that marks placeables in a string. Same as WithPlaceables but
 * with all the rules specific to the Fluent syntax at the beginning.
 *
 * The Fluent rules must come right after the space rules, otherwise it
 * generates a lot of false positives.
 */
const WithPlaceablesForFluent: any = createMarker(getRulesWithFluent(rules));

export default WithPlaceablesForFluent;

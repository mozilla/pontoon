/* @flow */

import './WithPlaceables.css';

import createMarker from 'lib/react-content-marker';

import { rules } from './WithPlaceables';
import unusualSpace from '../parsers/unusualSpace';


function getRulesWithoutUnusualSpace(rules: Array<Object>) {
    let newRules = [ ...rules ];
    newRules.splice(newRules.indexOf(unusualSpace), 1);
    return newRules;
}


const WithPlaceablesNoUnusualSpace = createMarker(getRulesWithoutUnusualSpace(rules));


export default WithPlaceablesNoUnusualSpace;

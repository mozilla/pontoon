/* @flow */

import './WithPlaceables.css';

import createMarker from 'lib/react-content-marker';

import escapeSequence from '../parsers/escapeSequence';
import multipleSpaces from '../parsers/multipleSpaces';
import narrowNonBreakingSpace from '../parsers/narrowNonBreakingSpace';
import newlineCharacter from '../parsers/newlineCharacter';
import nonBreakingSpace from '../parsers/nonBreakingSpace';
import pythonFormatString from '../parsers/pythonFormatString';
import tabCharacter from '../parsers/tabCharacter';
import thinSpace from '../parsers/thinSpace';
import unusualSpace from '../parsers/unusualSpace';


// Note: the order of these MATTERS!
const rules = [
    unusualSpace,
    nonBreakingSpace,
    narrowNonBreakingSpace,
    thinSpace,
    multipleSpaces,
    newlineCharacter,
    tabCharacter,
    pythonFormatString,
    escapeSequence,
];

const WithPlaceables = createMarker(rules);


export default WithPlaceables;

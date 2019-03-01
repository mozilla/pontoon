/* @flow */

import './WithPlaceables.css';

import createMarker from 'lib/react-content-marker';

import altAttribute from '../parsers/altAttribute';
import escapeSequence from '../parsers/escapeSequence';
import javaFormattingVariable from '../parsers/javaFormattingVariable';
import jsonPlaceholder from '../parsers/jsonPlaceholder';
import multipleSpaces from '../parsers/multipleSpaces';
import narrowNonBreakingSpace from '../parsers/narrowNonBreakingSpace';
import newlineCharacter from '../parsers/newlineCharacter';
import nonBreakingSpace from '../parsers/nonBreakingSpace';
import pythonFormatNamedString from '../parsers/pythonFormatNamedString';
import pythonFormatString from '../parsers/pythonFormatString';
import pythonFormattingVariable from '../parsers/pythonFormattingVariable';
import stringFormattingVariable from '../parsers/stringFormattingVariable';
import tabCharacter from '../parsers/tabCharacter';
import thinSpace from '../parsers/thinSpace';
import unusualSpace from '../parsers/unusualSpace';
import xmlEntity from '../parsers/xmlEntity';
import xmlTag from '../parsers/xmlTag';


// Note: the order of these MATTERS!
const rules = [
    newlineCharacter,
    tabCharacter,
    escapeSequence,
    unusualSpace,
    nonBreakingSpace,
    narrowNonBreakingSpace,
    thinSpace,
    multipleSpaces,
    xmlTag,
    altAttribute,
    xmlEntity,
    pythonFormatNamedString,
    pythonFormatString,
    pythonFormattingVariable,
    javaFormattingVariable,
    stringFormattingVariable,
    jsonPlaceholder,
];

const WithPlaceables = createMarker(rules);


export default WithPlaceables;

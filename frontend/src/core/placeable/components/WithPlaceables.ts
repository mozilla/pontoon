import createMarker from 'react-content-marker';

import './WithPlaceables.css';

import altAttribute from '../parsers/altAttribute';
import camelCaseString from '../parsers/camelCaseString';
import emailPattern from '../parsers/emailPattern';
import escapeSequence from '../parsers/escapeSequence';
import filePattern from '../parsers/filePattern';
import javaFormattingVariable from '../parsers/javaFormattingVariable';
import jsonPlaceholder from '../parsers/jsonPlaceholder';
import leadingSpace from '../parsers/leadingSpace';
import multipleSpaces from '../parsers/multipleSpaces';
import narrowNonBreakingSpace from '../parsers/narrowNonBreakingSpace';
import newlineCharacter from '../parsers/newlineCharacter';
import newlineEscape from '../parsers/newlineEscape';
import nonBreakingSpace from '../parsers/nonBreakingSpace';
import nsisVariable from '../parsers/nsisVariable';
import numberString from '../parsers/numberString';
import optionPattern from '../parsers/optionPattern';
import punctuation from '../parsers/punctuation';
import pythonFormatNamedString from '../parsers/pythonFormatNamedString';
import pythonFormatString from '../parsers/pythonFormatString';
import pythonFormattingVariable from '../parsers/pythonFormattingVariable';
import qtFormatting from '../parsers/qtFormatting';
import shortCapitalNumberString from '../parsers/shortCapitalNumberString';
import stringFormattingVariable from '../parsers/stringFormattingVariable';
import tabCharacter from '../parsers/tabCharacter';
import thinSpace from '../parsers/thinSpace';
import unusualSpace from '../parsers/unusualSpace';
import uriPattern from '../parsers/uriPattern';
import xmlEntity from '../parsers/xmlEntity';
import xmlTag from '../parsers/xmlTag';

// Note: the order of these MATTERS!
export const rules = [
    newlineEscape,
    newlineCharacter,
    tabCharacter,
    escapeSequence,

    // The spaces placeable can match '\n  ' and mask the newline,
    // so it has to come later.
    leadingSpace,
    unusualSpace,
    nonBreakingSpace,
    narrowNonBreakingSpace,
    thinSpace,
    multipleSpaces,

    // The XML placeables must be marked before variable placeables
    // to avoid marking variables, but leaving out tags. See:
    // https://bugzilla.mozilla.org/show_bug.cgi?id=1334926
    xmlTag,
    altAttribute,
    xmlEntity,

    pythonFormatNamedString,
    pythonFormatString,
    pythonFormattingVariable,
    javaFormattingVariable,
    stringFormattingVariable,
    // JSON Placeholder parser Must come before NSIS Variable parser,
    // otherwise JSON Placeholders are marked up without the trailing $
    jsonPlaceholder,
    nsisVariable,

    // The Qt variables can consume the %1 in %1$s which will mask a printf
    // placeable, so it has to come later.
    qtFormatting,

    uriPattern,
    filePattern,
    emailPattern,
    shortCapitalNumberString,
    camelCaseString,
    optionPattern,
    punctuation,
    numberString,
];

/**
 * Component that marks placeables in a string.
 */
const WithPlaceables: any = createMarker(rules);

export default WithPlaceables;

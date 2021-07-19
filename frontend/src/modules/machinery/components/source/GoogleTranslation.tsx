import * as React from 'react';
import { Localized } from '@fluent/react';
import { mark, Parser } from 'react-content-marker';
import { rules } from '../../../../core/placeable';
import { ReactNodeArray } from 'react';
import shajs from 'sha.js';

import xmlTag from '../../../../core/placeable/parsers/xmlTag';
import xmlEntity from '../../../../core/placeable/parsers/xmlEntity';
import punctuation from '../../../../core/placeable/parsers/punctuation';

/**
 * When the input format is html, remove the rules responsible for handling xml entities and xml tags because
 * Google Translate API is able to handle HTML/XML input.
 */
function getRulesBasedOnInputFormat(
    text: string,
    rules: Array<Parser>,
): Array<Parser> {
    let newRules: Array<Parser> = [...rules];

    if (GetGoogleTranslateInputFormat(text) === 'html') {
        newRules.splice(newRules.indexOf(xmlTag), 1);
        newRules.splice(newRules.indexOf(xmlEntity), 1);
    }

    // Don't pre-process the punctuation characters allowing GTA translate them.
    newRules.splice(newRules.indexOf(punctuation), 1);

    return newRules;
}

/**
 * Create a deterministic identifier for a placeable, using SHA256 and using the first 7 characters,
 * similarly to short commit hashes in Git.
 * Wishfully thinking there's no word that matches any of SHA256 hashes of placeables.
 */
function getPlaceableHash(placeable: string): string {
    return shajs('sha256').update(placeable).digest('hex').substring(0, 7);
}

/**
 * Detect the placeables and return them as array to process them later.
 */
export function GetPlaceables(searchString: string): Array<string> {
    let placeables: Array<string> = [];

    getRulesBasedOnInputFormat(searchString, rules).reduce(
        (acc: string | ReactNodeArray, parser: Parser): ReactNodeArray => {
            return mark(
                acc,
                parser.rule,
                (match: string): any => {
                    placeables.push(match);
                },
                parser['matchIndex'],
            );
        },
        searchString,
    );

    return placeables;
}

/**
 * Escape the special characters in order to pass the text later to RegExp.
 */
function escapeRegExp(text: string) {
    return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}

/**
 * Replace the placeables with their git-hashes in order to avoid breaking them by the Google Translate API.
 * The algorithm uses a RegExp in order to find all occurrences of placeables in order to replace them with their hashes.
 */
export function GetGoogleTranslateInputText(
    text: string,
    placeables: Array<string>,
): string {
    if (placeables.length == 0) {
        return text;
    }

    const placeablesRegex = new RegExp(
        '(' + placeables.map((x) => escapeRegExp(x)).join('|') + ')',
        'gi',
    );

    let newText: string = '';
    let placeableOccurrence = placeablesRegex.exec(text);
    let pos: number = 0;

    while (placeableOccurrence) {
        let placeable: string = placeableOccurrence[0];

        // Wrap the placeable with spaces, in order to avoid concatenating hashes of placeables with the words that
        // should be translated.
        // e.g.
        //   [disclaimer] $ is the end marker of the string.
        //
        //   Original string: On the nature of "daylight"$ # (only " is a placeable here)
        //   GTA input string: On the nature of <placeable hash>daylight<placeable hash>$
        //   ^ In such case, some of the words (e.g. daylight) won't be translated correctly.
        //   GTA output string [locale: pl]: O naturze 8a331fddaylight8a331fd$
        //   Final string visible in the Translate.Next UI: O naturze 8a331fddaylight8a331fd$
        //
        // However, when the placeables are separated:
        //   Original string: On the nature of "daylight" # (only " is a placeable here)
        //   GTA input string: On the nature of <placeable hash> daylight <placeable hash>
        //   ^ GTA is able to translate the words in this scenario.
        //   GTA output string [locale: pl]: O naturze <placeable hash> światła dziennego <placeable hash>
        //   ^ And that string is a correct translation without broken placeables, but has a different problem.
        //   Final string visible in the Translate.Next UI: O naturze " światła dziennego "$
        //
        // When spaces are added, GTA is able to translate the input, however that introduces additional
        // complexity related to restoring the original spacing between a placeable and its surrounding words/tokens.
        // e.g.
        //   Original string: On the nature of \n${something}  # (only ${something} is a placeable here)
        //   ^ Notice the lack of trailing spaces
        //   GTA input string: On the nature of \n <placeable hash> $
        //   ^ the pre-processing function added the trailing spaces. $ is the end marker of the string.
        //   GTA output string [locale: pl]: O naturze \n <placeable hash>$
        //   ^ GTA returns only the left trailing space. $ is the end marker of the string.
        //   Final string visible in the Translate.Next UI: O naturze \n ${something}$
        // Also, the direction of a script in a locale (LTR, RTL) is a factor that may change the order
        // of the placeables in a string and make restoring the surrounding spaces harder.

        newText +=
            text.substring(pos, placeableOccurrence.index) +
            ' ' +
            getPlaceableHash(placeable) +
            ' ';
        pos = placeableOccurrence.index + placeable.length;
        placeableOccurrence = placeablesRegex.exec(text);
    }

    if (pos < text.length - 1) {
        newText += text.substring(pos);
    }

    return newText;
}

/**
 * Google Translate API supports two input formats:
 * * text
 * * html
 * Depending on the selected format type, the API applies and returns format specific transformations,
 * e.g. replaces some reserved characters with HTML entities.
 */
export function GetGoogleTranslateInputFormat(text: string): 'text' | 'html' {
    // The regexes are borrowed from the corresponding placeable rules.
    const htmlEntities: RegExp = /(&(([a-zA-Z][a-zA-Z0-9.-]*)|([#](\d{1,5}|x[a-fA-F0-9]{1,5})+));)/;
    const htmlTags: RegExp = /(<[\w.:]+(\s([\w.:-]+=((".*?")|('.*?')))?)*\/?>|<\/[\w.]+>)/;

    if (text.search(htmlEntities) !== -1 || text.search(htmlTags) !== -1) {
        return 'html';
    }

    return 'text';
}

/**
 *  Process the response from the Google Translate API and replace the placeable hashes with their original values.
 *  Validate the translation and throw an error when a placeable is missing.
 */
export function GetGoogleTranslateResponseText(
    response: any,
    placeables: Array<string>,
): string | null {
    if (!response.translation) {
        throw new Error('No translation in response');
    }

    const checkAndReplace = (acc, placeable): string => {
        let placeableHash = getPlaceableHash(placeable);

        if (response.translation.indexOf(placeableHash) == -1) {
            throw new Error(
                `Google Translate API removed the placeable: ${placeable}`,
            );
        }
        return acc.replace(new RegExp(placeableHash, "gi"), placeable);
    };
    return placeables.reduce(checkAndReplace, response.translation);
}

/**
 * Show the translation source from Google Translate.
 */
export default function GoogleTranslation(): React.ReactElement<'li'> {
    return (
        <li>
            <Localized
                id='machinery-GoogleTranslation--visit-google'
                attrs={{ title: true }}
            >
                <a
                    className='translation-source'
                    href='https://translate.google.com/'
                    title='Visit Google Translate'
                    target='_blank'
                    rel='noopener noreferrer'
                    onClick={(e: React.MouseEvent) => e.stopPropagation()}
                >
                    <span>GOOGLE TRANSLATE</span>
                </a>
            </Localized>
        </li>
    );
}

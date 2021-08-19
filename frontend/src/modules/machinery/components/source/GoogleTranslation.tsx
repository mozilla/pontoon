import * as React from 'react';
import { Localized } from '@fluent/react';
import { mark, Parser } from 'react-content-marker';
import { rules } from '../../../../core/placeable';
import { ReactNodeArray } from 'react';

import xmlTag from 'core/placeable/parsers/xmlTag';
import xmlEntity from 'core/placeable/parsers/xmlEntity';
import punctuation from 'core/placeable/parsers/punctuation';
import numberString from 'core/placeable/parsers/numberString';

/**
 * When the input format is html, remove the rules responsible for handling xml entities and xml tags because
 * Google Translate API is able to handle HTML/XML input.
 */
function getRulesBasedOnInputFormat(rules: Array<Parser>): Array<Parser> {
    let newRules: Array<Parser> = [...rules];

    newRules.splice(newRules.indexOf(xmlTag), 1);
    newRules.splice(newRules.indexOf(xmlEntity), 1);

    // Don't pre-process the punctuation characters allowing GTA to translate them.
    newRules.splice(newRules.indexOf(punctuation), 1);
    newRules.splice(newRules.indexOf(numberString), 1);

    return newRules;
}

/**
 * Create a identifier for a placeable, based on its index from the placeables map,.
 * Additionally, encode information about the surrounding spaces.
 */
export function GetPlaceableHash(
    index: string,
    leftSpace: boolean,
    rightSpace: boolean,
): string {
    return `${leftSpace ? '1' : '0'}placeable${index}${rightSpace ? '1' : '0'}`;
}

/**
 * Detect the placeables and return them as array to process them later.
 */
export function GetPlaceables(searchString: string): Map<string, string> {
    let placeables: Map<string, string> = new Map<string, string>();
    let index: number = 0;
    getRulesBasedOnInputFormat(rules).reduce(
        (acc: string | ReactNodeArray, parser: Parser): ReactNodeArray => {
            return mark(
                acc,
                parser.rule,
                (match: string): any => {
                    if (!placeables.has(match)) {
                        placeables.set(match, (index++).toString());
                    }
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
 *
 * Wrap the placeable with spaces, in order to avoid concatenating hashes of placeables with the words that
 * should be translated.
 * e.g.
 *   [disclaimer] $ is the end marker of the string.
 *
 *   Original string: On the nature of "daylight"$ # (only " is a placeable here)
 *   GTA input string: On the nature of <placeable hash>daylight<placeable hash>$
 *   ^ In such case, some of the words (e.g. daylight) won't be translated correctly.
 *   GTA output string [locale: pl]: O naturze 8a331fddaylight8a331fd$
 *   Final string visible in the Translate.Next UI: O naturze 8a331fddaylight8a331fd$
 *
 * However, when the placeables are separated:
 *   Original string: On the nature of "daylight" # (only " is a placeable here)
 *   GTA input string: On the nature of <placeable hash> daylight <placeable hash>
 *   ^ GTA is able to translate the words in this scenario.
 *   GTA output string [locale: pl]: O naturze <placeable hash> światła dziennego <placeable hash>
 *   ^ And that string is a correct translation without broken placeables, but has a different problem.
 *   Final string visible in the Translate.Next UI: O naturze " światła dziennego "$
 *
 * When spaces are added, GTA is able to translate the input, however that introduces additional
 * complexity related to restoring the original spacing between a placeable and its surrounding words/tokens.
 * e.g.
 *   Original string: On the nature of \n${something}  # (only ${something} is a placeable here)
 *   ^ Notice the lack of trailing spaces
 *   GTA input string: On the nature of \n <placeable hash> $
 *   ^ the pre-processing function added the trailing spaces. $ is the end marker of the string.
 *   GTA output string [locale: pl]: O naturze \n <placeable hash>$
 *   ^ GTA returns only the left trailing space. $ is the end marker of the string.
 *   Final string visible in the Translate.Next UI: O naturze \n ${something}$
 */
export function GetGoogleTranslateInputText(
    text: string,
    placeablesMap: Map<string, string>,
): string {
    if (placeablesMap.size === 0) {
        return text;
    }
    const placeables: Array<string> = Array.from(placeablesMap.keys());
    const placeablesRegex = new RegExp(
        '(' + placeables.map((x) => escapeRegExp(x)).join('|') + ')',
        'gi',
    );

    let newText: string = '';
    let placeableOccurrence = placeablesRegex.exec(text);
    let pos: number = 0;

    while (placeableOccurrence) {
        let placeable: string = placeableOccurrence[0];

        let newPos = placeableOccurrence.index + placeable.length,
            textBefore = text.substring(pos, placeableOccurrence.index),
            textAfter = text.substring(newPos),
            leftSpace = textBefore[textBefore.length - 1] == ' ',
            rightSpace = textAfter[0] == ' ';

        newText +=
            textBefore +
            (leftSpace ? '' : ' ') +
            GetPlaceableHash(
                placeablesMap.get(placeableOccurrence[0]),
                leftSpace,
                rightSpace,
            ) +
            (rightSpace ? '' : ' ');
        pos = newPos;
        placeableOccurrence = placeablesRegex.exec(text);
    }

    if (pos < text.length - 1) {
        newText += text.substring(pos);
    }

    return newText.replace(/ {2}/gi, ' ').trim();
}

/**
 * Google Translate API supports two input formats:
 * * text
 * * html
 * Depending on the selected format type, GTA applies transformations like
 * e.g. replaces some reserved characters with HTML entities.
 */
export function GetGoogleTranslateInputFormat(text: string): 'text' | 'html' {
    if (text.search(xmlEntity.rule) !== -1 || text.search(xmlTag.rule) !== -1) {
        return 'html';
    }

    return 'text';
}

export function GoogleValidatePlaceables(
    text: string,
    placeablesMap: Map<string, string>,
): boolean {
    return Array.from(placeablesMap.keys()).every(
        (placeable) => text.indexOf(placeable) !== -1,
    );
}

/**
 *  Process the response from the Google Translate API and replace the placeable hashes with their original values.
 *  Validate the translation and throw an error when a placeable is missing.
 */
export function GetGoogleTranslateResponseText(
    text: string,
    placeablesMap: Map<string, string>,
    rightToLeft: boolean,
): string | null {
    if (placeablesMap.size == 0) {
        return text;
    }

    const inversePlaceablesMap = new Map(
        [...placeablesMap].map((item) => [item[1], item[0]]),
    );
    const isPunctuation = (text) => text.search(punctuation.rule) !== -1;
    const placeablesRegex = new RegExp(
        '( |)(?<leftSpace>0|1)placeable(?<placeableIndex>\\d+)(?<rightSpace>0|1)( |)',
        'gi',
    );

    let newText: string = '';
    let pos: number = 0;
    let placeableOccurrence = placeablesRegex.exec(text);

    while (placeableOccurrence) {
        let textBefore: string = text.substring(pos, placeableOccurrence.index),
            placeableOptions: any = placeableOccurrence.groups,
            leftSpace: boolean = placeableOptions.leftSpace === '1',
            rightSpace: boolean = placeableOptions.rightSpace === '1';

        if (!inversePlaceablesMap.has(placeableOptions.placeableIndex)) {
            throw new Error(
                `Placeable with an invalid index: ${placeableOptions.placeableIndex}`,
            );
        }

        if (rightToLeft) {
            [leftSpace, rightSpace] = [rightSpace, leftSpace];
        }

        newText += textBefore;
        if (
            leftSpace &&
            placeableOccurrence.index > 0 &&
            text[placeableOccurrence.index - 1] !== ' ' &&
            !isPunctuation(text[placeableOccurrence.index - 1])
        ) {
            newText += ' ';
        }

        newText += inversePlaceablesMap.get(placeableOptions.placeableIndex);
        pos = placeableOccurrence.index + placeableOccurrence[0].length;
        if (
            rightSpace &&
            pos < text.length &&
            text[pos] !== ' ' &&
            !isPunctuation(text[pos])
        ) {
            newText += ' ';
        }
        placeableOccurrence = placeablesRegex.exec(text);
    }

    if (pos < text.length - 1) {
        newText += text.substring(pos);
    }

    return newText;
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

/* @flow */

import { fluent } from 'core/utils';

import type { FluentMessage } from './types';
import type { Locale } from 'core/locale';

type SyntaxType = 'simple' | 'rich' | 'complex';

export function getSimpleFromComplex(
    current: string,
    original: string,
    initial: string,
): [string, string] {
    let translationContent = fluent.getSimplePreview(current);
    let initialContent = fluent.getSimplePreview(initial);

    // If any of the contents are junk, discard them.
    if (translationContent === current) {
        translationContent = '';
    }
    if (initialContent === initial) {
        initialContent = '';
    }

    return [translationContent, initialContent];
}

export function getComplexFromSimple(
    current: string,
    original: string,
    initial: string,
    locale: Locale,
): [string, string] {
    let initialContent = initial;

    const translationContent = fluent.serializer.serializeEntry(
        fluent.getReconstructedMessage(original, current),
    );

    // If there is no active translation (it's an untranslated string)
    // we make the initial translation an empty fluent message to avoid
    // showing unchanged content warnings.
    if (!initialContent) {
        initialContent = fluent.serializer.serializeEntry(
            fluent.getEmptyMessage(fluent.parser.parseEntry(original), locale),
        );
    }

    return [translationContent, initialContent];
}

export function getRichFromComplex(
    current: string,
    original: string,
    initial: string,
    locale: Locale,
): [FluentMessage, FluentMessage] {
    let translationContent = fluent.parser.parseEntry(current);

    // If the parsed content is invalid, create an empty message instead.
    // Note that this should be replaced with a check that prevents
    // turning back to the Rich editor, in order to avoid losing data.
    if (translationContent.type === 'Junk') {
        translationContent = fluent.getEmptyMessage(
            fluent.parser.parseEntry(original),
            locale,
        );
    }

    let initialContent = fluent.parser.parseEntry(initial);

    // If there is no active translation for this entity, create an
    // empty message to serve as the reference for unsaved changes.
    if (initialContent.type === 'Junk') {
        initialContent = fluent.getEmptyMessage(
            fluent.parser.parseEntry(original),
            locale,
        );
    }

    return [translationContent, initialContent];
}

export function getComplexFromRich(
    current: FluentMessage,
    original: string,
    initial: string,
    locale: Locale,
): [string, string] {
    let initialContent = initial;

    const translationContent = fluent.serializer.serializeEntry(current);

    // If there is no active translation (it's an untranslated string)
    // we make the initial translation an empty fluent message to avoid
    // showing unchanged content warnings.
    if (!initialContent) {
        initialContent = fluent.serializer.serializeEntry(
            fluent.getEmptyMessage(fluent.parser.parseEntry(original), locale),
        );
    }

    return [translationContent, initialContent];
}

/**
 * Update the content for the new type of form from the previous one. This
 * allows to keep changes made by the user when switching editing modes.
 *
 * @param {string} fromSyntax Syntax of the current translation.
 * @param {string} toSyntax Expected syntax of the output.
 * @param {string | FluentMessage} current Current content of the translation, as entered by the user.
 * @param {string} original Original string of the entity.
 * @param {string} initial Currently active translation, if any.
 *
 * @returns {[ string | FluentMessage, string ]} The converted current translation and initial translation.
 */
export default function convertSyntax(
    fromSyntax: SyntaxType,
    toSyntax: SyntaxType,
    current: string | FluentMessage,
    original: string,
    initial: string,
    locale: Locale,
) {
    if (
        fromSyntax === 'complex' &&
        toSyntax === 'simple' &&
        typeof current === 'string'
    ) {
        return getSimpleFromComplex(current, original, initial);
    } else if (
        fromSyntax === 'simple' &&
        toSyntax === 'complex' &&
        typeof current === 'string'
    ) {
        return getComplexFromSimple(current, original, initial, locale);
    } else if (
        fromSyntax === 'complex' &&
        toSyntax === 'rich' &&
        typeof current === 'string'
    ) {
        return getRichFromComplex(current, original, initial, locale);
    } else if (
        fromSyntax === 'rich' &&
        toSyntax === 'complex' &&
        typeof current !== 'string'
    ) {
        return getComplexFromRich(current, original, initial, locale);
    }

    throw new Error(
        `Unsupported conversion: from '${fromSyntax}' to '${toSyntax}'`,
    );
}

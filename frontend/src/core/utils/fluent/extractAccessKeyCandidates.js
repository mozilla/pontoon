/* @flow */

import flattenDeep from 'lodash.flattendeep';

import parser from './parser';
import serializer from './serializer';

import type { FluentMessage, PatternElement } from './types';


/**
 * Returns a flat list of Text Elements, either standalone or from SelectExpression variants
 */
function getTextElementsRecursivelly(elements: Array<PatternElement>) {
    const textElements = elements.map(element => {
        if (element.type === 'TextElement') {
            return element;
        }

        if (
            element.type === 'Placeable' &&
            element.expression && element.expression.type === 'SelectExpression'
        ) {
            return element.expression.variants.map(variant => {
                return getTextElementsRecursivelly(variant.value.elements);
            });
        }

        return null;
    });

    return flattenDeep(textElements);
}

/**
 * Return a list of potential access key candidates.
 *
 * The method first checks if the message contains an attribute with an ID 'accesskey',
 * and then generates a list of unique characters from either the attribute with an ID
 * 'label' or the message value.
 *
 * @param {FluentMessage} translation A Fluent message to extract access key candidates from.
 * @returns {?Array<string>} A list of access key candidates.
 */
export default function extractAccessKeyCandidates(translation: FluentMessage): ?Array<string> {
    // The input message is flat, so we must re-parse it to be able to remove non-TextElements
    let message = parser.parseEntry(serializer.serializeEntry(translation));

    // Unless it's Junk, which often happens while typing:
    // then it's better to still show some candidates then to show nothing
    if (message.type === 'Junk') {
        message = translation;
    }

    // If message has no attributes, return null
    if (!message.attributes) {
        return null;
    }

    const attributeIDs = message.attributes.map(attribute => attribute.id.name);

    // If message has no accesskey attribute, return null
    if (attributeIDs.indexOf('accesskey') === -1) {
        return null;
    }

    // Generate access key candidates from the 'label' attribute or the message value
    let source = null;
    if (message.attributes && attributeIDs.indexOf('label') !== -1) {
        source = message.attributes.find(attribute => attribute.id.name === 'label');
    }
    else if (message.value) {
        source = message;
    }

    if (!source || !source.value) {
        return null;
    }

    // Only take TextElements, see bug 1447103 for detals (that's why flat Message is no good)
    const textElements = getTextElementsRecursivelly(source.value.elements);

    // Collect values of TextElements
    const values = textElements.map(element => {
        let value = '';
        if (element && typeof(element.value) === 'string') {
            value = element.value.replace(/\s/g, '') // Also: Remove whitespace
        }
        return value;
    });

    // Create a list of single-character keys
    const keys = values.join('').split('');

    // Extract unique candidates
    return keys.filter((key, i, array) => array.indexOf(key) === i);
}

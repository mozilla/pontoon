/* @flow */

import { Transformer } from 'fluent-syntax';

import flattenMessage from './flattenMessage';
import isPluralElement from './isPluralElement';

import { CLDR_PLURALS } from 'core/plural';

import type { FluentMessage } from './types';
import type { Locale } from 'core/locale';


/**
 * Gather custom (numeric) plural variants
 */
function getNumericVariants(variants) {
    return variants.filter(variant => {
        return variant.key.type === 'NumberLiteral';
    });
}

/**
 * Generate a CLDR template variant
 */
function getCldrTemplateVariant(variants) {
    return variants.find(variant => {
        return CLDR_PLURALS.indexOf(variant.key.name) !== -1;
    });
}

/**
 * Generate locale plural variants from a template
 */
function getLocaleVariants(locale, template) {
    return locale.cldrPlurals.map(item => {
        const localeVariant = template.clone();
        localeVariant.key.name = CLDR_PLURALS[item];
        localeVariant.default = false;
        return localeVariant;
    });
}

/**
 * Return variants with default variant set
 */
function withDefaultVariant(variants) {
    const defaultVariant = variants.find(variant => {
        return variant.default === true;
    });

    if (!defaultVariant) {
        variants[variants.length-1].default = true;
    }

    return variants;
}

/**
 * Return a copy of a given Fluent AST with all its text elements empty.
 *
 * This makes a copy of the given Fluent message, then walks the copy and
 * replaces the content of each TextElement it finds with an empty string.
 *
 * Note that this produces "junk" Fluent messages. Serializing the AST works,
 * but parsing it afterwards will result in a Junk message.
 *
 * @param {FluentMessage} source A Fluent AST to empty.
 * @returns {FluentMessage} An emptied copy of the source.
 */
export default function getEmptyMessage(
    source: FluentMessage,
    locale: Locale,
): FluentMessage {
    class EmptyTransformer extends Transformer {
        visitTextElement(node) {
            node.value = '';
            return node;
        }
    }

    class PluralsTransformer extends Transformer {
        visitPlaceable(node) {
            if (isPluralElement(node)) {
                const variants = node.expression.variants;
                const numericVariants = getNumericVariants(variants);

                const template = getCldrTemplateVariant(variants);
                const localeVariants = template ? getLocaleVariants(locale, template) : [];

                node.expression.variants = withDefaultVariant(
                    numericVariants.concat(localeVariants)
                );
            }

            return node;
        }
    }

    const message = source.clone();

    // Convert all simple elements to TextElements
    const flatMessage = flattenMessage(message);

    // Empty TextElements
    const empty = new EmptyTransformer();
    const emptyMessage = empty.visit(flatMessage);

    // Create default locale plural variants
    const plurals = new PluralsTransformer();
    return plurals.visit(emptyMessage);
}

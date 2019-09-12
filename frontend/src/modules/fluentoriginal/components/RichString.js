/* @flow */

import * as React from 'react';
import { serializeVariantKey } from 'fluent-syntax';

import './RichString.css';

import { WithPlaceablesForFluent } from 'core/placeable';
import { fluent } from 'core/utils';

import type { Entity } from 'core/api';
import type {
    FluentAttribute,
    FluentAttributes,
    FluentElement,
    FluentValue,
} from 'core/utils/fluent/types';


type Props = {|
    +entity: Entity,
    +handleClickOnPlaceable: (SyntheticMouseEvent<HTMLParagraphElement>) => void,
|};


function renderItem(
    value: string,
    label: string,
    key: string,
    className: ?string,
): React.Node {
    return <tr key={ key } className={ className }>
        <td>
            <label>{ label }</label>
        </td>
        <td>
            <span>
                <WithPlaceablesForFluent>
                    { value }
                </WithPlaceablesForFluent>
            </span>
        </td>
    </tr>;
}


function renderElements(
    elements: Array<FluentElement>,
    label: string,
): React.Node {
    let indent = false;
    return elements.map((element, index) => {
        if (
            element.type === 'Placeable' &&
            element.expression && element.expression.type === 'SelectExpression'
        ) {
            const variantItems = element.expression.variants.map((variant, i) => {
                if (typeof(variant.value.elements[0].value) !== 'string') {
                    return null;
                }

                return renderItem(
                    variant.value.elements[0].value,
                    serializeVariantKey(variant.key),
                    [index, i].join('-'),
                    indent ? 'indented' : null,
                );
            });
            indent = false;
            return variantItems;
        }
        else {
            if (typeof(element.value) !== 'string') {
                return null;
            }

            indent = true;
            return renderItem(
                element.value,
                label,
                index.toString(),
            );
        }
    });
}


function renderValue(value: FluentValue, label?: string): React.Node {
    if (!value) {
        return null;
    }

    if (!label) {
        label = 'Value';
    }

    return renderElements(
        value.elements,
        label,
    );
}


function renderAttributes(attributes: ?FluentAttributes): React.Node {
    if (!attributes) {
        return null;
    }

    return attributes.map((attribute: FluentAttribute) => {
        return renderValue(
            attribute.value,
            attribute.id.name,
        );
    });
}


/**
 * Show the original string of a Fluent entity in a rich interface.
 */
export default function RichString(props: Props) {
    const message = fluent.flattenMessage(
        fluent.parser.parseEntry(props.entity.original)
    );

    return <table className="original fluent-rich-string" onClick={ props.handleClickOnPlaceable }>
        <tbody>
            { renderValue(message.value) }
            { renderAttributes(message.attributes) }
        </tbody>
    </table>;
}

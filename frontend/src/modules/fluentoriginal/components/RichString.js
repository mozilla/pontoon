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
): React.Node {
    return <tr key={ key }>
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
    return elements.map((element, index) => {
        if (element.type === 'Placeable' && element.expression.type === 'SelectExpression') {
            return element.expression.variants.map((variant, i) => {
                return renderItem(
                    variant.value.elements[0].value,
                    serializeVariantKey(variant.key),
                    [index, i].join('-'),
                );
            });
        }
        else {
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

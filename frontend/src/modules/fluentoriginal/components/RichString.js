/* @flow */

import * as React from 'react';

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


function renderElements(
    elements: Array<FluentElement>,
    label: string,
): React.Node {
    return elements.map((element) => {
        if (element.type !== 'TextElement') {
            return null;
        }

        return <tr>
            <td>
                <label>{ label }</label>
            </td>
            <td>
                <span>
                    <WithPlaceablesForFluent>
                        { element.value }
                    </WithPlaceablesForFluent>
                </span>
            </td>
        </tr>;
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
    const message = fluent.parser.parseEntry(props.entity.original);

    return <table className="original fluent-rich-string" onClick={ props.handleClickOnPlaceable }>
        <tbody>
            { renderValue(message.value) }
            { renderAttributes(message.attributes) }
        </tbody>
    </table>;
}

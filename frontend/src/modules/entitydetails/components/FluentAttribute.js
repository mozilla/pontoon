/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import { fluent } from 'core/utils';

import Property from './Property';

import type { Entity } from 'core/api';

type Props = {|
    +entity: Entity,
|};

/**
 * Get attribute of a simple single-attribute Fluent message.
 */
export default function FluentAttribute(props: Props) {
    const { entity } = props;

    if (entity.format !== 'ftl') {
        return null;
    }

    const message = fluent.parser.parseEntry(entity.original);

    if (!fluent.isSimpleSingleAttributeMessage(message)) {
        return null;
    }

    return (
        <Localized
            id='entitydetails-Metadata--attribute'
            attrs={{ title: true }}
        >
            <Property title='Attribute' className='attribute'>
                {message.attributes[0].id.name}
            </Property>
        </Localized>
    );
}

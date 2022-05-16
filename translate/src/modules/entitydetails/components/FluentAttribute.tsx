import React from 'react';
import { Localized } from '@fluent/react';

import type { Entity } from '~/api/entity';
import {
  isSimpleSingleAttributeMessage,
  parseEntry,
} from '~/core/utils/fluent';

import { Property } from './Property';

type Props = {
  readonly entity: Entity;
};

/**
 * Get attribute of a simple single-attribute Fluent message.
 */
export function FluentAttribute(props: Props): null | React.ReactElement<any> {
  const { entity } = props;

  if (entity.format !== 'ftl') {
    return null;
  }

  const message = parseEntry(entity.original);

  if (message.type !== 'Message' || !isSimpleSingleAttributeMessage(message)) {
    return null;
  }

  return (
    <Localized id='entitydetails-Metadata--attribute' attrs={{ title: true }}>
      <Property title='Attribute' className='attribute'>
        {message.attributes[0].id.name}
      </Property>
    </Localized>
  );
}

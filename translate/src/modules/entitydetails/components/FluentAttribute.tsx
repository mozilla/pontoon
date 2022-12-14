import React from 'react';
import { Localized } from '@fluent/react';

import type { Entity } from '~/api/entity';
import { isSimpleSingleAttributeMessage, parseEntry } from '~/utils/message';

import { Property } from './Property';

type Props = {
  readonly entity: Entity;
};

/**
 * Get attribute of a simple single-attribute Fluent message.
 */
export function FluentAttribute({
  entity: { format, original },
}: Props): null | React.ReactElement<any> {
  if (format !== 'ftl') {
    return null;
  }

  const message = parseEntry(original);

  return isSimpleSingleAttributeMessage(message) ? (
    <Localized id='entitydetails-Metadata--attribute' attrs={{ title: true }}>
      <Property title='Attribute' className='attribute'>
        {message.attributes[0].id.name}
      </Property>
    </Localized>
  ) : null;
}

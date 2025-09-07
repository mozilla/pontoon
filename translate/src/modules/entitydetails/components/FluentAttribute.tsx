import React from 'react';
import { Localized } from '@fluent/react';

import type { Entity } from '../../../api/entity';
import { parseEntry } from '../../../utils/message';

import { Property } from './Property';

type Props = {
  readonly entity: Entity;
};

/**
 * Get attribute of a simple single-attribute Fluent message.
 */
export function FluentAttribute({
  entity: { format, original },
}: Props): null | React.ReactElement {
  if (format !== 'fluent') {
    return null;
  }

  const entry = parseEntry(format, original);
  if (!entry || entry.value || entry.attributes?.size !== 1) {
    return null;
  }

  const [[name, attr]] = entry.attributes;
  return attr.type === 'message' ? (
    <Localized id='entitydetails-Metadata--attribute' attrs={{ title: true }}>
      <Property title='Attribute' className='attribute'>
        {name}
      </Property>
    </Localized>
  ) : null;
}

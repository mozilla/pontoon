import React from 'react';
import { Localized } from '@fluent/react';
import { isSelectMessage } from '@mozilla/l10n';

import type { MessageEntry } from '~/utils/message';

import { Property } from './Property';

/**
 * Get attribute of a simple single-attribute Fluent message.
 */
export function FluentAttribute({
  entry,
}: {
  readonly entry: MessageEntry | null;
}): null | React.ReactElement {
  if (!entry || entry.value || entry.attributes?.size !== 1) {
    return null;
  }

  const [[name, attr]] = entry.attributes;
  return !isSelectMessage(attr) ? (
    <Localized id='entitydetails-Metadata--attribute' attrs={{ title: true }}>
      <Property title='Attribute' className='attribute'>
        {name}
      </Property>
    </Localized>
  ) : null;
}

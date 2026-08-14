import React from 'react';

import {
  getPlainMessage,
  parseEntry,
  type MessageEntry,
} from '~/utils/message';

import { GenericTranslation } from './GenericTranslation';

type Props = {
  entry: MessageEntry | null;
  diffTarget?: string;
  search?: string | null;
};

export function Translation({
  entry,
  diffTarget,
  search,
}: Props): null | React.ReactElement<React.ElementType> {
  if (!entry) {
    return null;
  }

  const plain = getPlainMessage(entry);
  if (diffTarget) {
    const diffEntry = parseEntry(entry.format, diffTarget);
    if (diffEntry) {
      diffTarget = getPlainMessage(diffEntry);
    }
  }

  return (
    <GenericTranslation
      content={plain}
      diffTarget={diffTarget}
      search={search}
    />
  );
}

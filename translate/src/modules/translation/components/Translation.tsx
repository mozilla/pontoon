import React from 'react';

import { getPlainMessage, MessageEntry } from '~/utils/message';
import { specialFormats } from '~/utils/message/specialFormats';

import { GenericTranslation } from './GenericTranslation';

type Props = {
  content: string | MessageEntry | null;
  format?: string;
  diffTarget?: string;
  search?: string | null;
};

export function Translation({
  content,
  diffTarget,
  format,
  search,
}: Props): null | React.ReactElement<React.ElementType> {
  if (!content) {
    return null;
  }

  const plain = getPlainMessage(content, format);
  diffTarget &&= getPlainMessage(diffTarget, format);

  return (
    <GenericTranslation
      content={plain}
      diffTarget={diffTarget}
      search={search}
    />
  );
}

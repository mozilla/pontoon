import React from 'react';

import { getPlainMessage } from '~/utils/message';

import { GenericTranslation } from './GenericTranslation';
import { placeholderFormats } from '~/utils/message/placeholders';

type Props = {
  content: string;
  format: string;
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

  if (
    format === 'fluent' ||
    format === 'gettext' ||
    placeholderFormats.has(format)
  ) {
    content = getPlainMessage(content, format);
    diffTarget &&= getPlainMessage(diffTarget, format);
  }

  return (
    <GenericTranslation
      content={content}
      diffTarget={diffTarget}
      search={search}
    />
  );
}

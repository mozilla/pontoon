import React from 'react';

import { getPlainMessage } from '~/utils/message';
import { specialFormats } from '~/utils/message/specialFormats';

import { GenericTranslation } from './GenericTranslation';

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

  if (specialFormats.has(format)) {
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

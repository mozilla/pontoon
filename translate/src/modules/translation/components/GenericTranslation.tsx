import React from 'react';

import { TranslationDiff } from '~/modules/diff';
import { Highlight } from '~/modules/placeable/components/Highlight';

export type TranslationProps = {
  content: string;
  diffTarget?: string;
  search?: string | null;
};

export function GenericTranslation({
  content,
  diffTarget,
  search,
}: TranslationProps): React.ReactElement<React.ElementType> {
  if (diffTarget) {
    return <TranslationDiff base={diffTarget} target={content} />;
  }

  return <Highlight search={search}>{content}</Highlight>;
}

import React from 'react';

import { TranslationDiff } from '~/modules/diff';
import { Highlight } from '~/modules/placeable/components/Highlight';

export type TranslationProps = {
  content: string;
  diffTarget?: string;
  search?: string | null;
  translations_only?: boolean | null | undefined;
};

export function GenericTranslation({
  content,
  diffTarget,
  search,
  translations_only,
}: TranslationProps): React.ReactElement<React.ElementType> {
  if (diffTarget) {
    return <TranslationDiff base={diffTarget} target={content} />;
  }
  if (translations_only) {
    return <Highlight>{content}</Highlight>;
  }
  return <Highlight search={search}>{content}</Highlight>;
}

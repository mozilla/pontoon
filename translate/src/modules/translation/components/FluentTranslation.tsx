import React from 'react';

import { TranslationDiff } from '~/modules/diff';
import { Highlight } from '~/modules/placeable/components/Highlight';
import { getSimplePreview } from '~/utils/message';

import type { TranslationProps } from './GenericTranslation';

export function FluentTranslation({
  content,
  diffTarget,
  search,
  translations_only,
}: TranslationProps): React.ReactElement<React.ElementType> {
  const preview = getSimplePreview(content);

  if (diffTarget) {
    const fluentTarget = getSimplePreview(diffTarget);
    return <TranslationDiff base={fluentTarget} target={preview} />;
  }

  if (translations_only) {
    return <Highlight>{preview}</Highlight>;
  }
  return <Highlight search={search}>{preview}</Highlight>;
}

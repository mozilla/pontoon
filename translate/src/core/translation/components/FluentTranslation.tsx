import React from 'react';

import { TranslationDiff } from '~/core/diff';
import { Marked } from '~/core/placeable/components/Marked';
import { getSimplePreview } from '~/utils/message';
import { SearchTerms } from '~/modules/search';

import type { TranslationProps } from './GenericTranslation';

export function FluentTranslation({
  content,
  diffTarget,
  search,
}: TranslationProps): React.ReactElement<React.ElementType> {
  const preview = getSimplePreview(content);

  if (diffTarget) {
    const fluentTarget = getSimplePreview(diffTarget);
    return (
      <Marked fluent>
        <TranslationDiff base={fluentTarget} target={preview} />
      </Marked>
    );
  }

  if (search) {
    return (
      <Marked fluent>
        <SearchTerms search={search}>{preview}</SearchTerms>
      </Marked>
    );
  }

  return (
    <Marked fluent leadingSpaces>
      {preview}
    </Marked>
  );
}

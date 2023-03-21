import React from 'react';

import { TranslationDiff } from '~/modules/diff';
import { Highlight } from '~/modules/placeable/components/Highlight';
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
      <Highlight fluent>
        <TranslationDiff base={fluentTarget} target={preview} />
      </Highlight>
    );
  }

  if (search) {
    return (
      <Highlight fluent>
        <SearchTerms search={search}>{preview}</SearchTerms>
      </Highlight>
    );
  }

  return (
    <Highlight fluent leadingSpaces>
      {preview}
    </Highlight>
  );
}

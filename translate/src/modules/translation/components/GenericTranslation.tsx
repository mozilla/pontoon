import React from 'react';

import { TranslationDiff } from '~/modules/diff';
import { Highlight } from '~/modules/placeable/components/Highlight';
import { SearchTerms } from '~/modules/search';

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
    return (
      <Highlight>
        <TranslationDiff base={diffTarget} target={content} />
      </Highlight>
    );
  }

  if (search) {
    return (
      <Highlight>
        <SearchTerms search={search}>{content}</SearchTerms>
      </Highlight>
    );
  }

  return <Highlight leadingSpaces>{content}</Highlight>;
}

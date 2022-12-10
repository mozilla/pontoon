import React from 'react';

import { TranslationDiff } from '~/core/diff';
import { Marked } from '~/core/placeable/components/Marked';
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
      <Marked>
        <TranslationDiff base={diffTarget} target={content} />
      </Marked>
    );
  }

  if (search) {
    return (
      <Marked>
        <SearchTerms search={search}>{content}</SearchTerms>
      </Marked>
    );
  }

  return <Marked leadingSpaces>{content}</Marked>;
}

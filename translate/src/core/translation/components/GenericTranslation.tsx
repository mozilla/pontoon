import React from 'react';

import { TranslationDiff } from '~/core/diff';
import { WithPlaceables, WithPlaceablesNoLeadingSpace } from '~/core/placeable';
import { SearchTerms } from '~/modules/search';

export type TranslationProps = {
  content: string | null | undefined;
  diffTarget?: string | null | undefined;
  search?: string | null | undefined;
};

export function GenericTranslation({
  content,
  diffTarget,
  search,
}: TranslationProps): React.ReactElement<React.ElementType> {
  if (diffTarget) {
    return (
      <WithPlaceablesNoLeadingSpace>
        <TranslationDiff base={diffTarget} target={content ?? ''} />
      </WithPlaceablesNoLeadingSpace>
    );
  }

  if (search) {
    return (
      <WithPlaceablesNoLeadingSpace>
        <SearchTerms search={search}>{content ?? ''}</SearchTerms>
      </WithPlaceablesNoLeadingSpace>
    );
  }

  return <WithPlaceables>{content}</WithPlaceables>;
}

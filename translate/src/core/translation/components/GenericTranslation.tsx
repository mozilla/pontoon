import React from 'react';

import { TranslationDiff } from '~/core/diff';
import { WithPlaceables, WithPlaceablesNoLeadingSpace } from '~/core/placeable';
import { withSearch } from '~/modules/search';

const TranslationPlaceablesSearch = withSearch(WithPlaceablesNoLeadingSpace);

export type TranslationProps = {
  content: string | null | undefined;
  diffTarget?: string | null | undefined;
  search?: string | null | undefined;
};

export default function GenericTranslation({
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
      <TranslationPlaceablesSearch search={search}>
        {content}
      </TranslationPlaceablesSearch>
    );
  }

  return <WithPlaceables>{content}</WithPlaceables>;
}

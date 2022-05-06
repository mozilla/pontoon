import React from 'react';

import { TranslationDiff } from '~/core/diff';
import {
  WithPlaceablesForFluent,
  WithPlaceablesForFluentNoLeadingSpace,
} from '~/core/placeable';
import { getSimplePreview } from '~/core/utils/fluent';
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
      <WithPlaceablesForFluentNoLeadingSpace>
        <TranslationDiff base={fluentTarget} target={preview} />
      </WithPlaceablesForFluentNoLeadingSpace>
    );
  }

  if (search) {
    return (
      <WithPlaceablesForFluentNoLeadingSpace>
        <SearchTerms search={search}>{preview}</SearchTerms>
      </WithPlaceablesForFluentNoLeadingSpace>
    );
  }

  return <WithPlaceablesForFluent>{preview}</WithPlaceablesForFluent>;
}

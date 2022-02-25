import React from 'react';

import { TranslationDiff } from '~/core/diff';
import {
  WithPlaceablesForFluent,
  WithPlaceablesForFluentNoLeadingSpace,
} from '~/core/placeable';
import { fluent } from '~/core/utils';
import { SearchTerms } from '~/modules/search';

import type { TranslationProps } from './GenericTranslation';

export default function FluentTranslation({
  content,
  diffTarget,
  search,
}: TranslationProps): React.ReactElement<React.ElementType> {
  const preview = fluent.getSimplePreview(content);

  if (diffTarget) {
    const fluentTarget = fluent.getSimplePreview(diffTarget);
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

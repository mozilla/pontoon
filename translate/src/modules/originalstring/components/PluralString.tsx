import React, { useContext } from 'react';
import { Localized } from '@fluent/react';

import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { Highlight } from '~/modules/placeable/components/Highlight';
import type { TermState } from '~/modules/terms';

type Props = {
  onClick: (event: React.MouseEvent<HTMLElement>) => void;
  terms: TermState;
};

/**
 * Show the original string of an entity with plural forms.
 *
 * Based on the plural form, show either the singular or plural version of the
 * string, and also display which form is being rendered.
 */
export function PluralString({ onClick, terms }: Props): React.ReactElement {
  const { cldrPlurals } = useContext(Locale);
  const { entity, pluralForm } = useContext(EntityView);

  let title: React.ReactElement;
  let original: string;
  if (cldrPlurals[pluralForm] === 1) {
    title = (
      <Localized id='entitydetails-PluralString--singular'>
        <h2>SINGULAR</h2>
      </Localized>
    );
    original = entity.original;
  } else {
    title = (
      <Localized id='entitydetails-PluralString--plural'>
        <h2>PLURAL</h2>
      </Localized>
    );
    original = entity.original_plural;
  }

  return (
    <>
      {title}
      <p className='original' onClick={onClick}>
        <Highlight terms={terms}>{original}</Highlight>
      </p>
    </>
  );
}

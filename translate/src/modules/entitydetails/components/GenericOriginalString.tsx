import React, { useContext } from 'react';
import { Localized } from '@fluent/react';

import type { Entity } from '~/api/entity';
import { Locale } from '~/context/Locale';
import { getMarker, TermState } from '~/core/term';
import { EntityView } from '~/context/EntityView';

type Props = {
  entity: Entity;
  terms: TermState;
  handleClickOnPlaceable: (
    event: React.MouseEvent<HTMLParagraphElement>,
  ) => void;
};

/**
 * Show the original string of an entity.
 *
 * Based on the plural form, show either the singular or plural version of the
 * string, and also display which form is being rendered.
 */
export function GenericOriginalString({
  entity,
  handleClickOnPlaceable,
  terms,
}: Props): React.ReactElement {
  const { cldrPlurals } = useContext(Locale);
  const { hasPluralForms, pluralForm } = useContext(EntityView);

  let title: React.ReactElement | null;
  let original: string;
  if (!hasPluralForms) {
    title = null;
    original = entity.original;
  } else if (cldrPlurals[pluralForm] === 1) {
    title = (
      <Localized id='entitydetails-GenericOriginalString--singular'>
        <h2>SINGULAR</h2>
      </Localized>
    );
    original = entity.original;
  } else {
    title = (
      <Localized id='entitydetails-GenericOriginalString--plural'>
        <h2>PLURAL</h2>
      </Localized>
    );
    original = entity.original_plural;
  }

  const TermsAndPlaceablesMarker = getMarker(terms);
  return (
    <>
      {title}
      <p className='original' onClick={handleClickOnPlaceable}>
        <TermsAndPlaceablesMarker>{original}</TermsAndPlaceablesMarker>
      </p>
    </>
  );
}

import React, { useContext } from 'react';
import { Localized } from '@fluent/react';

import type { Entity } from '~/api/entity';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import type { TermState } from '~/core/term';
import { Marked } from '~/core/placeable/components/Marked';

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

  return (
    <>
      {title}
      <p className='original' onClick={handleClickOnPlaceable}>
        <Marked terms={terms}>{original}</Marked>
      </p>
    </>
  );
}

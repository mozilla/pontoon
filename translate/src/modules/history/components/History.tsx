import { Localized } from '@fluent/react';
import React, { useCallback, useContext } from 'react';

import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { useUpdateTranslationStatus } from '~/core/editor';
import { USER } from '~/core/user';
import { useAppDispatch, useAppSelector } from '~/hooks';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

import { deleteTranslation_ } from '../actions';
import { HISTORY } from '../reducer';
import './History.css';
import { Translation } from './Translation';

/**
 * Shows all existing translations of an entity.
 *
 * For each translation, show its author, date and status (approved, rejected).
 */
export function History(): React.ReactElement<'section'> | null {
  const dispatch = useAppDispatch();
  const { code } = useContext(Locale);
  const user = useAppSelector((state) => state[USER]);
  const isReadOnlyEditor = useReadonlyEditor();
  const { entity, hasPluralForms, pluralForm } = useContext(EntityView);
  const { fetching, translations } = useAppSelector((state) => state[HISTORY]);

  const pf = hasPluralForms ? pluralForm : -1;
  const deleteTranslation = useCallback(
    (translationId: number) =>
      dispatch(deleteTranslation_(entity.pk, code, pf, translationId)),
    [entity, code, pf],
  );
  const updateTranslationStatus = useUpdateTranslationStatus(false);

  if (!translations.length) {
    return fetching ? null : (
      <section className='history'>
        <Localized id='history-History--no-translations'>
          <p>No translations available.</p>
        </Localized>
      </section>
    );
  }

  return (
    <section className='history'>
      <ul id='history-list'>
        {translations.map((translation, index) => (
          <Translation
            translation={translation}
            activeTranslation={translations[0]}
            entity={entity}
            isReadOnlyEditor={isReadOnlyEditor}
            user={user}
            deleteTranslation={deleteTranslation}
            updateTranslationStatus={updateTranslationStatus}
            key={index}
            index={index}
          />
        ))}
      </ul>
    </section>
  );
}

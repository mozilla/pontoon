import { Localized } from '@fluent/react';
import React, { useCallback, useContext } from 'react';

import { Locale } from '~/context/Locale';
import { usePluralForm } from '~/context/PluralForm';
import { useUpdateTranslationStatus } from '~/core/editor';
import { useSelectedEntity } from '~/core/entities/hooks';
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
  const entity = useSelectedEntity();
  const { pluralForm } = usePluralForm(entity);
  const { fetching, translations } = useAppSelector((state) => state[HISTORY]);

  const deleteTranslation = useCallback(
    (translationId: number) =>
      dispatch(deleteTranslation_(entity?.pk, code, pluralForm, translationId)),
    [entity, code, pluralForm],
  );
  const updateTranslationStatus = useUpdateTranslationStatus(false);

  if (!entity || !translations.length) {
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

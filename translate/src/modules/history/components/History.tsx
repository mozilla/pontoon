import { Localized } from '@fluent/react';
import React, { useContext } from 'react';

import { EntityView } from '~/context/EntityView';
import { HistoryData, useDeleteTranslation } from '~/context/HistoryData';
import { useUpdateTranslationStatus } from '~/modules/editor';
import { USER } from '~/modules/user';
import { useAppSelector } from '~/hooks';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

import './History.css';
import { HistoryTranslationComponent } from './HistoryTranslation';

/**
 * Shows all existing translations of an entity.
 *
 * For each translation, show its author, date and status (approved, rejected).
 */
export function History(): React.ReactElement<'section'> | null {
  const user = useAppSelector((state) => state[USER]);
  const isReadOnlyEditor = useReadonlyEditor();
  const { entity } = useContext(EntityView);
  const { fetching, translations } = useContext(HistoryData);
  const deleteTranslation = useDeleteTranslation();
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
          <HistoryTranslationComponent
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

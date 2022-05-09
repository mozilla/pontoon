import { Localized } from '@fluent/react';
import React from 'react';

import type { Entity } from '~/api/entity';
import type { UserState } from '~/core/user';

import type { ChangeOperation, HistoryState } from '../index';
import './History.css';
import { Translation } from './Translation';

type Props = {
  entity: Entity;
  history: HistoryState;
  isReadOnlyEditor: boolean;
  user: UserState;
  deleteTranslation: (arg0: number) => void;
  updateEditorTranslation: (arg0: string, arg1: string) => void;
  updateTranslationStatus: (id: number, operation: ChangeOperation) => void;
};

/**
 * Shows all existing translations of an entity.
 *
 * For each translation, show its author, date and status (approved, rejected).
 */
export function History({
  entity,
  history: { fetching, translations },
  isReadOnlyEditor,
  user,
  deleteTranslation,
  updateEditorTranslation,
  updateTranslationStatus,
}: Props): React.ReactElement<'section'> | null {
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
            updateEditorTranslation={updateEditorTranslation}
            updateTranslationStatus={updateTranslationStatus}
            key={index}
            index={index}
          />
        ))}
      </ul>
    </section>
  );
}

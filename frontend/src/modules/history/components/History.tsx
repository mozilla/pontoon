import React from 'react';
import { Localized } from '@fluent/react';

import './History.css';

import Translation from './Translation';

import { Entity } from 'core/api';
import { Locale } from 'core/locale';
import { UserState } from 'core/user';
import { ChangeOperation, HistoryState } from '..';

type Props = {
    entity: Entity;
    history: HistoryState;
    isReadOnlyEditor: boolean;
    isTranslator: boolean;
    locale: Locale;
    user: UserState;
    deleteTranslation: (arg0: number) => void;
    addComment: (arg0: string, arg1: number | null | undefined) => void;
    updateEditorTranslation: (arg0: string, arg1: string) => void;
    updateTranslationStatus: (arg0: number, arg1: ChangeOperation) => void;
};

/**
 * Shows all existing translations of an entity.
 *
 * For each translation, show its author, date and status (approved, rejected).
 */
export default class History extends React.Component<Props> {
    renderNoResults() {
        return (
            <section className='history'>
                <Localized id='history-History--no-translations'>
                    <p>No translations available.</p>
                </Localized>
            </section>
        );
    }

    render() {
        const {
            entity,
            history,
            isReadOnlyEditor,
            isTranslator,
            locale,
            user,
            deleteTranslation,
            addComment,
            updateEditorTranslation,
            updateTranslationStatus,
        } = this.props;

        if (!history.translations.length) {
            if (history.fetching) {
                return null;
            }

            return this.renderNoResults();
        }

        return (
            <section className='history'>
                <ul id='history-list'>
                    {history.translations.map((translation, index) => {
                        return (
                            <Translation
                                translation={translation}
                                activeTranslation={history.translations[0]}
                                entity={entity}
                                isReadOnlyEditor={isReadOnlyEditor}
                                isTranslator={isTranslator}
                                locale={locale}
                                user={user}
                                deleteTranslation={deleteTranslation}
                                addComment={addComment}
                                updateEditorTranslation={
                                    updateEditorTranslation
                                }
                                updateTranslationStatus={
                                    updateTranslationStatus
                                }
                                key={index}
                                index={index}
                            />
                        );
                    })}
                </ul>
            </section>
        );
    }
}

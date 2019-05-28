/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './History.css';

import Translation from './Translation';

import type { Entity } from 'core/api';
import type { Locale } from 'core/locales';
import type { UserState } from 'core/user';
import type { ChangeOperation, HistoryState } from '..';


type Props = {|
    entity: Entity,
    history: HistoryState,
    isReadOnlyEditor: boolean,
    isTranslator: boolean,
    locale: Locale,
    user: UserState,
    deleteTranslation: (number) => void,
    updateEditorTranslation: (string) => void,
    updateTranslationStatus: (number, ChangeOperation) => void,
|};


/**
 * Shows all existing translations of an entity.
 *
 * For each translation, show its author, date and status (approved, rejected).
 */
export default class History extends React.Component<Props> {
    renderNoResults() {
        return <section className="history">
            <Localized id="history-history-no-translations">
                <p>No translations available.</p>
            </Localized>
        </section>
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
            updateEditorTranslation,
            updateTranslationStatus,
        } = this.props;

        if (!history.translations.length) {
            if (history.fetching) {
                return null;
            }

            return this.renderNoResults();
        }

        return <section className="history">
            <ul>
                { history.translations.map((translation, index) => {
                    return <Translation
                        translation={ translation }
                        activeTranslation={ history.translations[0] }
                        entity={ entity }
                        isReadOnlyEditor={ isReadOnlyEditor }
                        canReview={ isTranslator }
                        locale={ locale }
                        user={ user }
                        deleteTranslation={ deleteTranslation }
                        updateEditorTranslation={ updateEditorTranslation }
                        updateTranslationStatus={ updateTranslationStatus }
                        key={ index }
                        index={ index }
                    />;
                }) }
            </ul>
        </section>;
    }
}

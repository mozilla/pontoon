/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './OtherLocales.css';

import Translation from './Translation';

import type { OtherLocaleTranslation } from 'core/api';
import type { Navigation } from 'core/navigation';
import type { UserState } from 'core/user';
import type { DbEntity } from 'modules/entitieslist';
import type { LocalesState } from '..';


type Props = {|
    entity: DbEntity,
    isReadOnlyEditor: boolean,
    orderedOtherLocales: Array<OtherLocaleTranslation>,
    preferredLocalesCount: number,
    otherlocales: LocalesState,
    parameters: Navigation,
    user: UserState,
    updateEditorTranslation: (string) => void,
|};


/**
 * Shows all translations of an entity in locales other than the current one.
 */
export default class OtherLocales extends React.Component<Props> {
    renderNoResults() {
        return <section className="other-locales">
            <Localized id="history-history-no-translations">
                <p>No translations available.</p>
            </Localized>
        </section>
    }

    render() {
        const {
            entity,
            isReadOnlyEditor,
            orderedOtherLocales,
            preferredLocalesCount,
            otherlocales,
            parameters,
            updateEditorTranslation,
        } = this.props;

        if (otherlocales.fetching) {
            return null;
        }

        if (!otherlocales.translations.length) {
            return this.renderNoResults();
        }

        return <section className="other-locales">
            <ul>
                { orderedOtherLocales.map((translation, index) => {
                    let lastPreferred = (index === preferredLocalesCount - 1);

                    return <Translation
                        entity={ entity }
                        isReadOnlyEditor={ isReadOnlyEditor }
                        translation={ translation }
                        parameters={ parameters }
                        updateEditorTranslation={ updateEditorTranslation }
                        lastPreferred={ lastPreferred }
                        key={ index }
                    />;
                }) }
            </ul>
        </section>;
    }
}

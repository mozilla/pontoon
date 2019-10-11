/* @flow */

import React from 'react';
import { Localized } from '@fluent/react';

import './OtherLocales.css';

import Translation from './Translation';

import type { Entity, OtherLocaleTranslation } from 'core/api';
import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';
import type { LocalesState } from '..';


type Props = {|
    entity: Entity,
    isReadOnlyEditor: boolean,
    orderedOtherLocales: Array<OtherLocaleTranslation>,
    preferredLocalesCount: number,
    otherlocales: LocalesState,
    parameters: NavigationParams,
    user: UserState,
    updateEditorTranslation: (string, string) => void,
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

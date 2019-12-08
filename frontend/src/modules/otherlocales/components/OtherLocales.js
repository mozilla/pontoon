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

    renderTranslations(
        translation: OtherLocaleTranslation,
        index: number,
        lastPreferred: boolean,
    ) {
        return <Translation
            entity={ this.props.entity }
            isReadOnlyEditor={ this.props.isReadOnlyEditor }
            translation={ translation }
            parameters={ this.props.parameters }
            updateEditorTranslation={ this.props.updateEditorTranslation }
            lastPreferred = { lastPreferred }
            key={ index }
        />;
    }

    render() {
        const { otherlocales } = this.props;

        if (!otherlocales.translations) {
            return null;
        }

        const translation = otherlocales.translations;
        const preferredCount = translation.preferred.length;

        if (otherlocales.fetching) {
            return null;
        }

        if (!translation.other.length && !translation.preferred.length) {
            return this.renderNoResults();
        }

        return <section>
            <section className="other-locales">
                <ul>
                    { translation.preferred.map((translation, index) => {
                        const lastPreferred = (index === preferredCount -1);

                        return this.renderTranslations(
                            translation,
                            index,
                            lastPreferred,
                        );
                    }) }
                </ul>
                <ul>
                    { translation.other.map((translation, index) => {
                        const lastPreferred = false;

                        return this.renderTranslations(
                            translation,
                            index,
                            lastPreferred,
                        );
                    }) }
                </ul>
            </section>
        </section>;
    }
}

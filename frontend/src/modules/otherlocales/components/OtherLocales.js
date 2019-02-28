/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './OtherLocales.css';

import api from 'core/api';
import Translation from './Translation';

import type { Navigation } from 'core/navigation';
import type { LocalesState } from '..';
import type { UserState } from 'core/user';


type Props = {|
    orderedOtherLocales: Array<api.types.OtherLocaleTranslation>,
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

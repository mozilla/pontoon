/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './Locales.css';

import Translation from './Translation';

import type { Navigation } from 'core/navigation';
import type { LocalesState } from '..';
import type { UserState } from 'core/user';


type Props = {|
    otherlocales: LocalesState,
    user: UserState,
    parameters: Navigation,
    updateEditorTranslation: (string) => void,
    preferredCount: number,
|};


/**
 * Shows all translations of an entity in locales other than the current one.
 */
export default class Locales extends React.Component<Props> {
    /**
     * Orders the list of locales. The list starts with prefered locales,
     * in order as they are defined. The remaining locales follow in the
     * given (alphabetic) order.
     */
    sortByPreferred() {
        const { otherlocales, user } = this.props;
        const translations = otherlocales.translations;

        if (!user.isAuthenticated) {
            return translations;
        }

        const preferredLocales = user.preferredLocales.reverse();

        return translations.sort((a, b) => {
            let indexA = preferredLocales.indexOf(a.code);
            let indexB = preferredLocales.indexOf(b.code);

            if (indexA === -1 && indexB === -1) {
                return a > b;
            }
            else if (indexA < indexB) {
                return 1;
            }
            else if (indexA > indexB) {
                return -1;
            }
            else {
                return 0;
            }
        });
    }

    renderNoResults() {
        return <section className="other-locales">
            <Localized id="history-history-no-translations">
                <p>No translations available.</p>
            </Localized>
        </section>
    }

    render() {
        const {
            otherlocales,
            parameters,
            updateEditorTranslation,
            preferredCount,
        } = this.props;

        if (otherlocales.fetching) {
            return null;
        }

        if (!otherlocales.translations.length) {
            return this.renderNoResults();
        }

        const translations = this.sortByPreferred();

        return <section className="other-locales">
            <ul>
                { translations.map((translation, index) => {
                    let lastPreferred = (index === preferredCount - 1);

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

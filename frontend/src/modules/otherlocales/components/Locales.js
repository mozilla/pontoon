/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './Locales.css';

import Translation from './Translation';

import type { Navigation } from 'core/navigation';
import type { LocalesState } from '..';


type Props = {|
    otherlocales: LocalesState,
    parameters: Navigation,
    updateEditorTranslation: (string) => void,
|};


/**
 * Shows all translations of an entity in locales other than the current one.
 */
export default class Locales extends React.Component<Props> {
    renderNoResults() {
        return <section className="other-locales">
            <Localized id="history-history-no-translations">
                <p>No translations available.</p>
            </Localized>
        </section>
    }

    render() {
        const { otherlocales, parameters, updateEditorTranslation } = this.props;

        if (otherlocales.fetching) {
            return null;
        }

        if (!otherlocales.translations.length) {
            return this.renderNoResults();
        }

        return <section className="other-locales">
            <ul>
                { otherlocales.translations.map((translation, key) => {
                    return <Translation
                        translation={ translation }
                        parameters={ parameters }
                        updateEditorTranslation={ updateEditorTranslation }
                        key={ key }
                    />;
                }) }
            </ul>
        </section>;
    }
}

/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './Locales.css';

import type { Navigation } from 'core/navigation';
import type { LocalesState } from '..';


type Props = {|
    otherlocales: LocalesState,
    parameters: Navigation,
|};


/**
 * Shows all translations of an entity in locales other than the current one.
 */
export default class Locales extends React.Component<Props> {
    renderNoResults() {
        return <section className="otherlocales">
            <Localized id="history-history-no-translations">
                <p>No translations available.</p>
            </Localized>
        </section>
    }

    render() {
        const { otherlocales, parameters } = this.props;

        if (otherlocales.fetching) {
            return null;
        }

        if (!otherlocales.translations.length) {
            return this.renderNoResults();
        }

        return <section className="other-locales">
            <ul>
                { otherlocales.translations.map((translation, key) => {
                    return <li key={ key }>
                        <header>
                            <a
                                href={ `/translate/${translation.code}/${parameters.project}/${parameters.resource}/?string=${parameters.entity}` }
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                { translation.locale }
                                <span>{ translation.code }</span>
                            </a>
                        </header>
                        <p
                            lang={ translation.code }
                            dir={ translation.direction }
                            script={ translation.script }
                        >
                            { translation.translation }
                        </p>
                    </li>;
                }) }
            </ul>
        </section>;
    }
}

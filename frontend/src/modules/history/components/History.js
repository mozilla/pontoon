/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './History.css';

import Translation from './Translation';
import type { HistoryState } from '..';


type Props = {|
    history: HistoryState,
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
        const { history } = this.props;

        if (history.fetching) {
            return null;
        }

        if (!history.translations.length) {
            return this.renderNoResults();
        }

        return <section className="history">
            <ul>
                { history.translations.map((translation, key) => {
                    return <Translation translation={ translation } key={ key } />;
                }) }
            </ul>
        </section>;
    }
}

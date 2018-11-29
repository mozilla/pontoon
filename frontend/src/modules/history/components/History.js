/* @flow */

import React from 'react';
import { Localized } from 'fluent-react';

import './History.css';

import Translation from './Translation';
import { actions } from '..';
import type { DBTranslation, HistoryState } from '../reducer';


type Props = {|
    history: HistoryState,
|};


/**
 * Shows all existing translations of an entity.
 *
 * For each translation, show its author, date and status (approved, rejected).
 */
<<<<<<< HEAD
export default class History extends React.Component<Props> {
=======
export class HistoryBase extends React.Component<InternalProps> {
    fetchHistory() {
        const { parameters, pluralForm, dispatch } = this.props;

        // This is a newly selected entity, remove the previous history
        // then fetch the history of the new entity.
        dispatch(actions.reset());
        dispatch(actions.get(
            parameters.entity,
            parameters.locale,
            pluralForm,
        ));
    }

    componentDidMount() {
        this.fetchHistory();
    }

    componentDidUpdate(prevProps: InternalProps) {
        if (
            this.props.parameters.entity !== prevProps.parameters.entity ||
            this.props.pluralForm !== prevProps.pluralForm
        ) {
            this.fetchHistory();
        }
    }

    updateTranslationStatus = (translation: DBTranslation, change: string) => {
        const { parameters, pluralForm, dispatch } = this.props;
        dispatch(actions.updateStatus(
            change,
            parameters.entity,
            parameters.locale,
            parameters.resource,
            pluralForm,
            translation.pk,
        ));
    }

>>>>>>> Bug 1490351 - Add actions on status icons in History tab.
    renderNoResults() {
        return <section className="history">
            <Localized id="history-history-no-translations">
                <p>No translations available.</p>
            </Localized>
        </section>
    }

    render() {
        const { history } = this.props;

        if (!history.translations.length) {
            if (history.fetching) {
                return null;
            }

            return this.renderNoResults();
        }

        return <section className="history">
            <ul>
                { history.translations.map((translation, key) => {
                    return <Translation
                        translation={ translation }
                        updateTranslationStatus={ this.updateTranslationStatus }
                        key={ key }
                    />;
                }) }
            </ul>
        </section>;
    }
}

/* @flow */

import React from 'react';
import { connect } from 'react-redux';
import { Localized } from 'fluent-react/compat';

import './History.css';

import { selectors as navSelectors } from 'core/navigation';
import * as plural from 'core/plural';

import Translation from './Translation';
import { actions, NAME } from '..';
import type { HistoryState } from '../reducer';

import type { Navigation } from 'core/navigation';


type Props = {|
    history: HistoryState,
    parameters: Navigation,
    pluralForm: number,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};

/**
 * Shows all existing translations of an entity.
 *
 * For each translation, show its author, date and status (approved, rejected).
 */
export class HistoryBase extends React.Component<InternalProps> {
    fetchHistory() {
        const { parameters, pluralForm, dispatch } = this.props;

        // This is a newly selected entity, remove the previous history
        // then fetch the history of the new entity.
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


const mapStateToProps = (state: Object): Props => {
    return {
        history: state[NAME],
        parameters: navSelectors.getNavigation(state),
        pluralForm: plural.selectors.getPluralForm(state),
    };
};

export default connect(mapStateToProps)(HistoryBase);

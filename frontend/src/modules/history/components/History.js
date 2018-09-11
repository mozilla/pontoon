/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import './History.css';

import { selectors as navSelectors } from 'core/navigation';

import Translation from './Translation';
import { actions, NAME } from '..';
import type { HistoryState } from '../reducer';

import type { Navigation } from 'core/navigation';


type Props = {|
    history: HistoryState,
    parameters: Navigation,
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
        const { history, parameters, dispatch } = this.props;

        if (history.entity !== parameters.entity) {
            // This is a newly selected entity, remove the previous history
            // then fetch the history of the new entity.
            dispatch(actions.get(parameters.entity, parameters.locale));
        }
    }

    componentDidMount() {
        this.fetchHistory();
    }

    componentDidUpdate() {
        this.fetchHistory();
    }

    render() {
        const { history } = this.props;

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
    };
};

export default connect(mapStateToProps)(HistoryBase);

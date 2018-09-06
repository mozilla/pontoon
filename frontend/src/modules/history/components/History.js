/* @flow */

import React from 'react';
import { connect } from 'react-redux';

import './History.css';

import { selectors as navSelectors } from 'core/navigation';

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
            // This is a newly selected entity, fetch its history.
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

        return <div>
            { history.translations.map((translation, i) => <p>
                { translation.string }
            </p>) }
        </div>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        history: state[NAME],
        parameters: navSelectors.getNavigation(state),
    };
};

export default connect(mapStateToProps)(HistoryBase);

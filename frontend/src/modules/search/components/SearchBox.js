/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import debounce from 'lodash.debounce';

import './SearchBox.css';

import {
    actions as navActions,
    selectors as navSelectors,
} from 'core/navigation';
import type { Navigation } from 'core/navigation';
import { NAME as STATS_NAME } from 'core/stats';
import type { Stats } from 'core/stats';

import { FILTERS_STATUS } from '..';
import FiltersPanel from './FiltersPanel';


type Props = {|
    parameters: Navigation,
    stats: Stats,
    router: Object,
|};

type InternalProps = {|
    ...Props,
    dispatch: Function,
|};

type State = {|
    search: string,
|};


/**
 * Shows and controls a search box, used to filter the list of entities.
 *
 * Changes to the search input will be reflected in the URL. The user input
 * on that field is debounced, an update of the UI will only be triggered
 * after some time has passed since the last key stroke.
 */
export class SearchBoxBase extends React.Component<InternalProps, State> {
    constructor(props: InternalProps) {
        super(props);

        const search = props.parameters.search;
        this.state = {
            search: search ? search.toString() : '',
        };
    }

    updateSearchInput = (event: SyntheticInputEvent<HTMLInputElement>) => {
        this.setState({
            search: event.currentTarget.value,
        }, () => this.updateSearchParams());
    }

    updateSearchParams = debounce(() => {
        this.props.dispatch(navActions.updateSearch(this.props.router, this.state.search));
    }, 500)

    selectStatus = (status: ?string) => {
        this.props.dispatch(navActions.updateStatus(this.props.router, status));
    }

    render() {
        const { parameters, stats } = this.props;

        let selectedStatus = FILTERS_STATUS.find(
            item => item.tag === parameters.status
        );
        if (!selectedStatus) {
            selectedStatus = { title: 'All' };
        }
        const placeholder = `Search in ${selectedStatus.title}`;

        return <div className="search-box clearfix">
            <label htmlFor="search">
                <div className="fa fa-search"></div>
            </label>
            <input
                id="search"
                autoComplete="off"
                placeholder={ placeholder }
                title="Search Strings (Ctrl + Shift + F)"
                type="search"
                value={ this.state.search }
                onChange={ this.updateSearchInput }
            />
            <FiltersPanel
                stats={ stats }
                parameters={ parameters }
                selectStatus={ this.selectStatus }
            />
        </div>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        parameters: navSelectors.getNavigation(state),
        stats: state[STATS_NAME],
        router: state.router,
    };
};

export default connect(mapStateToProps)(SearchBoxBase);

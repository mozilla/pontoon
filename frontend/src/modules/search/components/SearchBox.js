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
        const { stats } = this.props;

        return <div className="search-box">
            <label htmlFor="search">
                <div className="icon fa fa-search"></div>
            </label>
            <input
                id="search"
                autoComplete="off"
                placeholder="Search in All"
                title="Search Strings (Ctrl + Shift + F)"
                type="search"
                value={ this.state.search }
                onChange={ this.updateSearchInput }
            />
            <FiltersPanel stats={ stats } selectStatus={ this.selectStatus } />
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

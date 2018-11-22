/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import debounce from 'lodash.debounce';

import './SearchBox.css';

import { selectors as navSelectors } from 'core/navigation';
import type { Navigation } from 'core/navigation';

import { actions } from '..';


type Props = {|
    parameters: Navigation,
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
        this.props.dispatch(actions.update(this.state.search, this.props.router));
    }, 500)

    render() {
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
        </div>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        parameters: navSelectors.getNavigation(state),
        router: state.router,
    };
};

export default connect(mapStateToProps)(SearchBoxBase);

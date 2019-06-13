/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import debounce from 'lodash.debounce';

import './SearchBox.css';

import * as navigation from 'core/navigation';
import { NAME as STATS_NAME } from 'core/stats';
import * as unsavedchanges from 'modules/unsavedchanges';

import { FILTERS_STATUS } from '..';
import FiltersPanel from './FiltersPanel';

import type { NavigationParams } from 'core/navigation';
import type { Stats } from 'core/stats';
import type { UnsavedChangesState } from 'modules/unsavedchanges';


type Props = {|
    parameters: NavigationParams,
    stats: Stats,
    router: Object,
    unsavedchanges: UnsavedChangesState,
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
    searchInput: { current: ?HTMLInputElement };

    constructor(props: InternalProps) {
        super(props);

        const search = props.parameters.search;
        this.state = {
            search: search ? search.toString() : '',
        };

        this.searchInput = React.createRef();
    }

    componentDidMount() {
        // $FLOW_IGNORE (errors that I don't understand, no help from the Web)
        document.addEventListener('keydown', this.handleShortcuts);
    }

    componentDidUpdate(prevProps: InternalProps) {
        // Clear search field when navigating to a new file
        if (
            this.props.parameters.search === null &&
            prevProps.parameters.search !== null
        ) {
            this.setState({
                search: '',
            });
        }
    }

    componentWillUnmount() {
        // $FLOW_IGNORE (errors that I don't understand, no help from the Web)
        document.removeEventListener('keydown', this.handleShortcuts);
    }

    handleShortcuts = (event: SyntheticKeyboardEvent<>) => {
        const key = event.keyCode;

        // On Ctrl + Shift + F, set focus on the search input.
        if (key === 70 && !event.altKey && event.ctrlKey && event.shiftKey) {
            event.preventDefault();
            if (this.searchInput.current) {
                this.searchInput.current.focus();
            }
        }
    }

    updateSearchInput = (event: SyntheticInputEvent<HTMLInputElement>) => {
        this.setState({
            search: event.currentTarget.value,
        }, () => this.updateSearchParams());
    }

    updateSearchParams = debounce(() => {
        const { dispatch, router } = this.props;

        dispatch(
            unsavedchanges.actions.check(
                this.props.unsavedchanges,
                () => {
                    dispatch(
                        navigation.actions.updateSearch(
                            router,
                            this.state.search,
                        )
                    );
                }
            )
        );
    }, 500)

    selectStatus = (status: ?string) => {
        const { dispatch, router } = this.props;

        dispatch(
            unsavedchanges.actions.check(
                this.props.unsavedchanges,
                () => {
                    dispatch(
                        navigation.actions.updateStatus(
                            router,
                            status,
                        )
                    );
                }
            )
        );
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
                ref={ this.searchInput }
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
        parameters: navigation.selectors.getNavigationParams(state),
        stats: state[STATS_NAME],
        router: state.router,
        unsavedchanges: state[unsavedchanges.NAME],
    };
};

export default connect(mapStateToProps)(SearchBoxBase);

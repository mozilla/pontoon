/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import debounce from 'lodash.debounce';

import './SearchBox.css';

import * as navigation from 'core/navigation';
import { NAME as STATS_NAME } from 'core/stats';
import * as unsavedchanges from 'modules/unsavedchanges';

import { FILTERS_STATUS, FILTERS_EXTRA } from '..';
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
    statuses: { [string]: boolean },
    extras: { [string]: boolean },
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

        const statuses = this.getInitialStatuses();
        if (props.parameters.status) {
            props.parameters.status.split(',').forEach(f => {
                statuses[f] = true;
            });
        }

        const extras = this.getInitialExtras();
        if (props.parameters.extra) {
            props.parameters.extra.split(',').forEach(f => {
                extras[f] = true;
            });
        }

        this.state = {
            search: search ? search.toString() : '',
            statuses,
            extras,
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

    getInitialStatuses() {
        const statuses = {};
        FILTERS_STATUS.forEach(s => statuses[s.slug] = false);
        return statuses;
    }

    getInitialExtras() {
        const extras = {};
        FILTERS_EXTRA.forEach(e => extras[e.slug] = false);
        return extras;
    }

    getSelectedStatuses(): Array<string> {
        return Object.keys(this.state.statuses).filter(s => this.state.statuses[s]);
    }

    getSelectedExtras(): Array<string> {
        return Object.keys(this.state.extras).filter(e => this.state.extras[e]);
    }

    toggleFilter = (filter: string) => {
        let type;
        if (filter in this.getInitialStatuses()) {
            type = 'statuses';
        }
        else if (filter in this.getInitialExtras()) {
            type = 'extras';
        }

        this.setState(state => {
            return {
                [type]: {
                    ...state[type],
                    [filter]: !state[type][filter],
                },
            };
        });
    }

    applySingleFilter = (filter: string, callback?: () => void) => {
        const statuses = this.getInitialStatuses();
        const extras = this.getInitialExtras();

        if (filter !== 'all') {
            if (filter in statuses) {
                statuses[filter] = true;
            }
            else if (filter in extras) {
                extras[filter] = true;
            }
        }

        if (callback) {
            this.setState({ statuses, extras }, callback);
        }
        else {
            this.setState({ statuses, extras });
        }
    }

    resetFilters = () => {
        this.setState({
            statuses: this.getInitialStatuses(),
            extras: this.getInitialExtras(),
        });
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
        this.update();
    }, 500)

    _update = () => {
        const statuses = this.getSelectedStatuses();
        let status = statuses.join(',');

        if (status === 'all') {
            status = null;
        }

        const extras = this.getSelectedExtras();
        const extra = extras.join(',');

        this.props.dispatch(
            navigation.actions.update(
                this.props.router,
                {
                    search: this.state.search,
                    status,
                    extra,
                },
            )
        );
    }

    update = () => {
        this.props.dispatch(
            unsavedchanges.actions.check(
                this.props.unsavedchanges,
                this._update,
            )
        )
    }

    composePlaceholder() {
        const selectedStatuses = FILTERS_STATUS.filter(
            f => this.getSelectedStatuses().includes(f.slug)
        );

        const selectedExtras = FILTERS_EXTRA.filter(
            f => this.getSelectedExtras().includes(f.slug)
        );

        let selectedFilters = [].concat(
            selectedStatuses,
            selectedExtras,
        );

        if (!selectedFilters.length) {
            selectedFilters = [{ title: 'All' }];
        }

        const selectedFiltersString = selectedFilters.map(item => item.title).join(', ');

        return `Search in ${selectedFiltersString}`;
    }

    render() {
        const { stats } = this.props;

        return <div className="search-box clearfix">
            <label htmlFor="search">
                <div className="fa fa-search"></div>
            </label>
            <input
                id="search"
                ref={ this.searchInput }
                autoComplete="off"
                placeholder={ this.composePlaceholder() }
                title="Search Strings (Ctrl + Shift + F)"
                type="search"
                value={ this.state.search }
                onChange={ this.updateSearchInput }
            />
            <FiltersPanel
                statuses={ this.state.statuses }
                extras={ this.state.extras }
                stats={ stats }
                applySingleFilter={ this.applySingleFilter }
                resetFilters={ this.resetFilters }
                toggleFilter={ this.toggleFilter }
                update={ this.update }
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

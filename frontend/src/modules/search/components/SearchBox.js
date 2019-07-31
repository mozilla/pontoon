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
    statuses: { [string]: boolean },
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

        const statuses =  this.getInitialStatuses();
        if (props.parameters.status) {
            props.parameters.status.split(',').forEach(f => {
                statuses[f] = true;
            });
        }

        this.state = {
            search: search ? search.toString() : '',
            statuses,
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
        FILTERS_STATUS.forEach(s => statuses[s.tag] = false);
        return statuses;
    }

    getSelectedStatuses(): Array<string> {
        return Object.keys(this.state.statuses).filter(s => this.state.statuses[s]);
    }

    toggleStatus = (status: string) => {
        this.setState(state => {
            return {
                statuses: {
                    ...state.statuses,
                    [status]: !state.statuses[status],
                },
            };
        });
    }

    setSingleStatus = (status: string, callback?: () => void) => {
        const statuses = this.getInitialStatuses();
        if (status !== 'all') {
            statuses[status] = true;
        }
        if (callback) {
            this.setState({ statuses }, callback);
        }
        else {
            this.setState({ statuses });
        }
    }

    resetStatuses = () => {
        this.setState({ statuses: this.getInitialStatuses() });
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
        const statuses = Object.keys(this.state.statuses).filter(f => this.state.statuses[f]);
        let status = statuses.join(',');

        if (status === 'all') {
            status = null;
        }

        this.props.dispatch(
            navigation.actions.update(
                this.props.router,
                {
                    search: this.state.search,
                    status,
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

    render() {
        const { stats } = this.props;

        const statuses = this.getSelectedStatuses();
        let selectedStatuses = FILTERS_STATUS.filter(
            item => statuses.includes(item.tag)
        );
        if (!selectedStatuses.length) {
            selectedStatuses = [{ title: 'All' }];
        }

        const statusesStr = selectedStatuses.map(item => item.title).join(', ');
        const placeholder = `Search in ${statusesStr}`;

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
                statuses={ this.state.statuses }
                stats={ stats }
                resetStatuses={ this.resetStatuses }
                setSingleStatus={ this.setSingleStatus }
                toggleStatus={ this.toggleStatus }
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

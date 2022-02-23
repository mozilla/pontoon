import * as React from 'react';
import isEqual from 'lodash.isequal';

import './SearchBox.css';

import { AppStore, useAppDispatch, useAppSelector, useAppStore } from '~/hooks';
import * as editor from '~/core/editor';
import * as navigation from '~/core/navigation';
import * as entities from '~/core/entities';
import { NAME as PROJECT_NAME } from '~/core/project';
import { NAME as STATS_NAME } from '~/core/stats';
import * as search from '~/modules/search';
import * as unsavedchanges from '~/modules/unsavedchanges';

import { FILTERS_STATUS, FILTERS_EXTRA } from '../constants';
import FiltersPanel from './FiltersPanel';

import type { AppDispatch } from '~/store';
import type { NavigationParams } from '~/core/navigation';
import type { ProjectState } from '~/core/project';
import type { Stats } from '~/core/stats';
import type { SearchAndFilters } from '~/modules/search';

export type TimeRangeType = {
  from: number;
  to: number;
};

type Props = {
  searchAndFilters: SearchAndFilters;
  parameters: NavigationParams;
  project: ProjectState;
  stats: Stats;
  router: Record<string, any>;
};

type InternalProps = Props & {
  store: AppStore;
  dispatch: AppDispatch;
};

type State = {
  search: string;
  statuses: Record<string, boolean>;
  extras: Record<string, boolean>;
  tags: Record<string, boolean>;
  timeRange: TimeRangeType | null | undefined;
  authors: Record<string, boolean>;
};

export type FilterType =
  | 'authors'
  | 'extras'
  | 'statuses'
  | 'tags'
  | 'timeRange';

/**
 * Shows and controls a search box, used to filter the list of entities.
 *
 * Changes to the search input will be reflected in the URL.
 */
export class SearchBoxBase extends React.Component<InternalProps, State> {
  searchInput = React.createRef<HTMLInputElement>();

  state: State = {
    search: '',
    statuses: {},
    extras: {},
    tags: {},
    timeRange: null,
    authors: {},
  };

  updateFiltersFromURLParams = () => {
    const { author, extra, status, tag, time } = this.props.parameters;

    const next = this.getInitState();
    if (author) for (const a of author.split(',')) next.authors[a] = true;
    if (extra) for (const e of extra.split(',')) next.extras[e] = true;
    if (status) for (const s of status.split(',')) next.statuses[s] = true;
    if (tag) for (const t of tag.split(',')) next.tags[t] = true;
    if (time) next.timeRange = this.getTimeRangeFromURLParameter(time);

    this.setState(next);
  };

  componentDidMount() {
    document.addEventListener('keydown', this.handleShortcuts);
    this.updateFiltersFromURLParams();

    // On mount, update the search input content based on URL.
    // This is not in the `updateFiltersFromURLParams` method because we want to
    // do this *only* on mount. The behavior is slightly different on update.
    const searchParam = this.props.parameters.search;
    this.setState({
      search: searchParam ? searchParam.toString() : '',
    });
  }

  componentDidUpdate(prevProps: InternalProps) {
    const { parameters } = this.props;
    // Clear search field when navigating to a new file
    if (parameters.search === null && prevProps.parameters.search !== null) {
      this.setState({ search: '' });
    }

    // When the URL changes, for example from links in the ResourceProgress
    // component, reload the filters from the URL parameters.
    if (parameters !== prevProps.parameters) this.updateFiltersFromURLParams();
  }

  componentWillUnmount() {
    document.removeEventListener('keydown', this.handleShortcuts);
  }

  getTimeRangeFromURLParameter(timeParameter: string): TimeRangeType {
    const [from, to] = timeParameter.split('-');
    return { from: parseInt(from), to: parseInt(to) };
  }

  getInitState() {
    const { project, searchAndFilters } = this.props;
    const state: Omit<State, 'search'> = {
      authors: {},
      extras: {},
      statuses: {},
      tags: {},
      timeRange: null,
    };

    for (const { email } of searchAndFilters.authors)
      state.authors[email] = false;
    for (const { slug } of FILTERS_EXTRA) state.extras[slug] = false;
    for (const { slug } of FILTERS_STATUS) state.statuses[slug] = false;
    for (const { slug } of project.tags) state.tags[slug] = false;

    return state;
  }

  updateTimeRange = (filter: string) => {
    this.setState({ timeRange: this.getTimeRangeFromURLParameter(filter) });
  };

  toggleFilter = (filter: string, type: FilterType) => {
    if (type === 'timeRange') {
      let timeRange: State['timeRange'] =
        this.getTimeRangeFromURLParameter(filter);

      if (isEqual(timeRange, this.state.timeRange)) {
        timeRange = null;
      }

      this.setState({ timeRange });
    } else {
      this.setState((state) => {
        const prev = state[type][filter];
        return { ...state, [type]: { ...state[type], [filter]: !prev } };
      });
    }
  };

  applySingleFilter = (
    filter: string,
    type: FilterType,
    callback: () => void,
  ) => {
    const next = this.getInitState();
    if (filter !== 'all') {
      if (type === 'timeRange')
        next.timeRange = this.getTimeRangeFromURLParameter(filter);
      else next[type][filter] = true;
    }
    this.setState(next, callback);
  };

  resetFilters = () => {
    this.setState(this.getInitState());
  };

  getAuthorsAndTimeRangeData = () => {
    const { locale, project, resource } = this.props.parameters;
    this.props.dispatch(
      search.actions.getAuthorsAndTimeRangeData(locale, project, resource),
    );
  };

  handleShortcuts = (event: KeyboardEvent) => {
    // On Ctrl + Shift + F, set focus on the search input.
    if (
      event.keyCode === 70 &&
      !event.altKey &&
      event.ctrlKey &&
      event.shiftKey
    ) {
      event.preventDefault();
      if (this.searchInput.current) {
        this.searchInput.current.focus();
      }
    }
  };

  unsetFocus = () => {
    this.props.dispatch(search.actions.setFocus(false));
  };

  setFocus = () => {
    this.props.dispatch(search.actions.setFocus(true));
  };

  updateSearchInput = (event: React.SyntheticEvent<HTMLInputElement>) => {
    this.setState({
      search: event.currentTarget.value,
    });
  };

  handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    // Perform search on Enter
    if (event.keyCode === 13) {
      this.update();
    }
  };

  _update = () => {
    const { authors, extras, search, statuses, tags, timeRange } = this.state;

    let status: string | null = Object.keys(statuses)
      .filter((s) => statuses[s])
      .join(',');
    if (status === 'all') status = null;

    const author = Object.keys(authors).filter((a) => authors[a]);
    const extra = Object.keys(extras).filter((e) => extras[e]);
    const tag = Object.keys(tags).filter((t) => tags[t]);
    const time = timeRange ? `${timeRange.from}-${timeRange.to}` : '';

    this.props.dispatch(entities.actions.reset());
    this.props.dispatch(editor.actions.reset());
    this.props.dispatch(
      navigation.actions.update(this.props.router, {
        author: author.join(','),
        extra: extra.join(','),
        search,
        status,
        tag: tag.join(','),
        time,
      }),
    );
  };

  update = () => {
    const state = this.props.store.getState();
    const unsavedChangesExist = state[unsavedchanges.NAME].exist;
    const unsavedChangesIgnored = state[unsavedchanges.NAME].ignored;

    this.props.dispatch(
      unsavedchanges.actions.check(
        unsavedChangesExist,
        unsavedChangesIgnored,
        this._update,
      ),
    );
  };

  composePlaceholder(): string {
    const { project, searchAndFilters } = this.props;
    const { authors, extras, statuses, tags, timeRange } = this.state;

    const selected: string[] = [];
    for (const { name, slug } of FILTERS_STATUS)
      if (statuses[slug]) selected.push(name);
    for (const { name, slug } of FILTERS_EXTRA)
      if (extras[slug]) selected.push(name);
    for (const { name, slug } of project.tags)
      if (tags[slug]) selected.push(name);
    if (timeRange) selected.push('Time Range');
    for (const { display_name, email } of searchAndFilters.authors)
      if (authors[email]) selected.push(`${display_name}'s translations`);

    const str = selected.length > 0 ? selected.join(', ') : 'All';
    return `Search in ${str}`;
  }

  render(): React.ReactElement<'div'> {
    const { searchAndFilters, parameters, project, stats } = this.props;

    return (
      <div className='search-box clearfix'>
        <label htmlFor='search'>
          <div className='fa fa-search'></div>
        </label>
        <input
          id='search'
          ref={this.searchInput}
          autoComplete='off'
          placeholder={this.composePlaceholder()}
          title='Search Strings (Ctrl + Shift + F)'
          type='search'
          value={this.state.search}
          onBlur={this.unsetFocus}
          onChange={this.updateSearchInput}
          onFocus={this.setFocus}
          onKeyDown={this.handleKeyDown}
        />
        <FiltersPanel
          statuses={this.state.statuses}
          extras={this.state.extras}
          tags={this.state.tags}
          timeRange={this.state.timeRange}
          authors={this.state.authors}
          tagsData={project.tags}
          timeRangeData={searchAndFilters.countsPerMinute}
          authorsData={searchAndFilters.authors}
          stats={stats}
          parameters={parameters}
          applySingleFilter={this.applySingleFilter}
          getAuthorsAndTimeRangeData={this.getAuthorsAndTimeRangeData}
          resetFilters={this.resetFilters}
          toggleFilter={this.toggleFilter}
          update={this.update}
          updateTimeRange={this.updateTimeRange}
          updateFiltersFromURLParams={this.updateFiltersFromURLParams}
        />
      </div>
    );
  }
}

export default function SearchBox(): React.ReactElement<typeof SearchBoxBase> {
  const state = {
    searchAndFilters: useAppSelector((state) => state[search.NAME]),
    parameters: useAppSelector((state) =>
      navigation.selectors.getNavigationParams(state),
    ),
    project: useAppSelector((state) => state[PROJECT_NAME]),
    stats: useAppSelector((state) => state[STATS_NAME]),
    router: useAppSelector((state) => state.router),
  };

  return (
    <SearchBoxBase
      {...state}
      dispatch={useAppDispatch()}
      store={useAppStore()}
    />
  );
}

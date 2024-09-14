import React, {
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useReducer,
  useRef,
  useState,
} from 'react';

import { Location } from '~/context/Location';
import { UnsavedActions } from '~/context/UnsavedChanges';
import { resetEntities } from '~/modules/entities/actions';
import { ProjectState, useProject } from '~/modules/project';
import { useAppDispatch, useAppSelector } from '~/hooks';
import type { SearchAndFilters } from '~/modules/search';
import { SEARCH } from '~/modules/search';
import type { AppDispatch } from '~/store';

import { getAuthorsAndTimeRangeData } from '../actions';
import { FILTERS_EXTRA, FILTERS_STATUS } from '../constants';

import { FiltersPanel } from './FiltersPanel';
import { SearchPanel } from './SearchPanel';
import './SearchBox.css';

export type TimeRangeType = {
  from: number;
  to: number;
};

type Props = {
  searchAndFilters: SearchAndFilters;
  parameters: Location;
  project: ProjectState;
};

type InternalProps = Props & {
  dispatch: AppDispatch;
};

export type FilterType = 'authors' | 'extras' | 'statuses' | 'tags';

export type SearchType =
  | 'search_identifiers'
  | 'search_translations_only'
  | 'search_rejected_translations'
  | 'search_match_case'
  | 'search_match_whole_word';

function getTimeRangeFromURL(timeParameter: string): TimeRangeType {
  const [from, to] = timeParameter.split('-');
  return { from: parseInt(from), to: parseInt(to) };
}

export type FilterState = {
  authors: string[];
  extras: string[];
  statuses: string[];
  tags: string[];
};

export type FilterAction = {
  filter: FilterType;
  value: string | string[] | null | undefined;
};

export type SearchState = {
  search_identifiers: boolean;
  search_translations_only: boolean;
  search_rejected_translations: boolean;
  search_match_case: boolean;
  search_match_whole_word: boolean;
};

export type SearchAction = {
  searchOption: SearchType;
  value: boolean | null | undefined;
};

/** If SearchBox has focus, translation form updates should not grab focus for themselves.  */
export const searchBoxHasFocus = () => document.activeElement?.id === 'search';

/**
 * Shows and controls a search box, used to filter the list of entities.
 *
 * Changes to the search input will be reflected in the URL.
 */
export function SearchBoxBase({
  dispatch,
  parameters,
  project,
  searchAndFilters,
}: InternalProps): React.ReactElement<'div'> {
  const { checkUnsavedChanges } = useContext(UnsavedActions);
  const applyOnChange = useRef(false);
  const searchInput = useRef<HTMLInputElement>(null);
  const [search, setSearch] = useState('');
  const [timeRange, setTimeRange] = useReducer(
    (_prev: unknown, value: string | null | undefined) =>
      value ? getTimeRangeFromURL(value) : null,
    null,
  );
  const [filters, updateFilters] = useReducer(
    (state: FilterState, action: FilterAction[]) => {
      const next = { ...state };
      for (const { filter, value } of action) {
        next[filter] = Array.isArray(value)
          ? value
          : typeof value === 'string'
          ? value.split(',')
          : [];
      }
      return next;
    },
    {
      authors: [],
      extras: [],
      statuses: [],
      tags: [],
    },
  );

  const [searchOptions, updateSearchOptions] = useReducer(
    (state: SearchState, action: SearchAction[]) => {
      const next = { ...state };
      for (const { searchOption, value } of action) {
        next[searchOption] = value ?? false;
      }
      return next;
    },
    {
      search_identifiers: false,
      search_translations_only: false,
      search_rejected_translations: false,
      search_match_case: false,
      search_match_whole_word: false,
    },
  );

  useEffect(() => {
    const handleShortcuts = (ev: KeyboardEvent) => {
      // On Ctrl + Shift + F, set focus on the search input.
      if (ev.key === 'F' && !ev.altKey && ev.ctrlKey && ev.shiftKey) {
        ev.preventDefault();
        searchInput.current?.focus();
      }
    };
    document.addEventListener('keydown', handleShortcuts);
    return () => document.removeEventListener('keydown', handleShortcuts);
  }, []);

  const updateFiltersFromURL = useCallback(() => {
    const { author, extra, status, tag, time } = parameters;
    updateFilters([
      { filter: 'authors', value: author },
      { filter: 'extras', value: extra },
      { filter: 'statuses', value: status },
      { filter: 'tags', value: tag },
    ]);
    setTimeRange(time);
  }, [parameters]);

  const updateOptionsFromURL = useCallback(() => {
    const {
      search_identifiers,
      search_translations_only,
      search_rejected_translations,
      search_match_case,
      search_match_whole_word,
      time,
    } = parameters;
    updateSearchOptions([
      { searchOption: 'search_identifiers', value: search_identifiers },
      {
        searchOption: 'search_translations_only',
        value: search_translations_only,
      },
      {
        searchOption: 'search_rejected_translations',
        value: search_rejected_translations,
      },
      {
        searchOption: 'search_match_case',
        value: search_match_case,
      },
      {
        searchOption: 'search_match_whole_word',
        value: search_match_whole_word,
      },
    ]);
    setTimeRange(time);
  }, [parameters]);

  // When the URL changes, for example from links in the ResourceProgress
  // component, reload the filters and search options from the URL parameters.
  useEffect(updateFiltersFromURL, [parameters]);
  useEffect(updateOptionsFromURL, [parameters]);

  const mounted = useRef(false);
  useEffect(() => {
    // On mount, update the search input content based on URL.
    // This is not in the `updateFiltersFromURLParams` method because we want to
    // do this *only* on mount. The behavior is slightly different on update.
    if (mounted.current) {
      if (parameters.search == null) {
        setSearch('');
      }
    } else {
      setSearch(parameters.search ?? '');
      mounted.current = true;
    }
  }, [parameters.search]);

  const toggleFilter = useCallback(
    (value: string, filter: FilterType) => {
      const next = [...filters[filter]];
      const prev = next.indexOf(value);
      if (prev === -1) {
        next.push(value);
      } else {
        next.splice(prev, 1);
      }
      updateFilters([{ filter, value: next }]);
    },
    [filters],
  );

  const toggleOption = useCallback(
    (searchOption: SearchType) => {
      const next = !searchOptions[searchOption];
      updateSearchOptions([{ searchOption, value: next }]);
    },
    [searchOptions],
  );

  const resetFilters = useCallback(() => {
    updateFilters([
      { filter: 'authors', value: [] },
      { filter: 'extras', value: [] },
      { filter: 'statuses', value: [] },
      { filter: 'tags', value: [] },
    ]);
    setTimeRange(null);
  }, []);

  const applySingleFilter = useCallback(
    (value: string, filter: FilterType | 'timeRange') => {
      resetFilters();
      applyOnChange.current = true;
      if (filter === 'timeRange') {
        setTimeRange(value);
      } else {
        updateFilters([{ filter, value }]);
      }
    },
    [],
  );

  const handleGetAuthorsAndTimeRangeData = useCallback(() => {
    const { locale, project, resource } = parameters;
    dispatch(getAuthorsAndTimeRangeData(locale, project, resource));
  }, [parameters]);

  const applyOptions = useCallback(
    () =>
      checkUnsavedChanges(() => {
        const {
          search_identifiers,
          search_translations_only,
          search_rejected_translations,
          search_match_case,
          search_match_whole_word,
        } = searchOptions;
        dispatch(resetEntities());
        parameters.push({
          ...parameters, // Persist all other variables to next state
          search_identifiers: search_identifiers,
          search_translations_only: search_translations_only,
          search_rejected_translations: search_rejected_translations,
          search_match_case: search_match_case,
          search_match_whole_word: search_match_whole_word,
          entity: 0, // With the new results, the current entity might not be available anymore.
        });
      }),
    [dispatch, parameters, search, searchOptions],
  );

  const applyFilters = useCallback(
    () =>
      checkUnsavedChanges(() => {
        const { authors, extras, statuses, tags } = filters;

        let status: string | null = statuses.join(',');
        if (status === 'all') {
          status = null;
        }

        dispatch(resetEntities());
        parameters.push({
          author: authors.join(','),
          extra: extras.join(','),
          search,
          status,
          tag: tags.join(','),
          time: timeRange ? `${timeRange.from}-${timeRange.to}` : null,
          entity: 0, // With the new results, the current entity might not be available anymore.
          list: null,
        });
      }),
    [dispatch, parameters, search, filters],
  );

  useEffect(() => {
    if (applyOnChange.current) {
      applyOnChange.current = false;
      applyFilters();
    }
  }, [filters, timeRange]);

  const placeholder = useMemo(() => {
    const { authors, extras, statuses, tags } = filters;

    const selected: string[] = [];
    for (const { name, slug } of FILTERS_STATUS) {
      if (statuses.includes(slug)) {
        selected.push(name);
      }
    }
    for (const { name, slug } of FILTERS_EXTRA) {
      if (extras.includes(slug)) {
        selected.push(name);
      }
    }
    for (const { name, slug } of project.tags) {
      if (tags.includes(slug)) {
        selected.push(name);
      }
    }
    if (timeRange) {
      selected.push('Time Range');
    }
    for (const { display_name, email } of searchAndFilters.authors) {
      if (authors.includes(email)) {
        selected.push(`${display_name}'s translations`);
      }
    }

    const str = selected.length > 0 ? selected.join(', ') : 'All';
    return `Search in ${str}`;
  }, [filters, project.tags, searchAndFilters.authors, timeRange]);

  return (
    <div className='search-box clearfix'>
      <input
        id='search'
        ref={searchInput}
        autoComplete='off'
        placeholder={placeholder}
        title='Search Strings (Ctrl + Shift + F)'
        type='search'
        value={search}
        onChange={(ev) => setSearch(ev.currentTarget.value)}
        onKeyDown={(ev) => {
          if (ev.key === 'Enter') {
            applyFilters();
          }
        }}
      />
      <FiltersPanel
        filters={filters}
        tagsData={project.tags}
        timeRange={timeRange}
        timeRangeData={searchAndFilters.countsPerMinute}
        authorsData={searchAndFilters.authors}
        parameters={parameters}
        applyFilters={applyFilters}
        applySingleFilter={applySingleFilter}
        getAuthorsAndTimeRangeData={handleGetAuthorsAndTimeRangeData}
        resetFilters={resetFilters}
        toggleFilter={toggleFilter}
        setTimeRange={setTimeRange}
        updateFiltersFromURL={updateFiltersFromURL}
      />
      <SearchPanel
        searchOptions={searchOptions}
        applyOptions={applyOptions}
        toggleOption={toggleOption}
        updateOptionsFromURL={updateOptionsFromURL}
      />
    </div>
  );
}

export function SearchBox(): React.ReactElement<typeof SearchBoxBase> {
  const state = {
    searchAndFilters: useAppSelector((state) => state[SEARCH]),
    parameters: useContext(Location),
    project: useProject(),
  };

  return <SearchBoxBase {...state} dispatch={useAppDispatch()} />;
}

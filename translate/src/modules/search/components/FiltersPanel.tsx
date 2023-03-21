import { Localized } from '@fluent/react';
import classNames from 'classnames';
import React, { useCallback, useEffect, useMemo, useState } from 'react';

import type { Author } from '~/api/filter';
import type { Tag } from '~/api/project';
import type { Location } from '~/context/Location';
import { Stats, useStats } from '~/modules/stats';
import { asLocaleString, useOnDiscard } from '~/utils';

import { FILTERS_EXTRA, FILTERS_STATUS } from '../constants';
import './FiltersPanel.css';
import type { FilterState, FilterType, TimeRangeType } from './SearchBox';
import { TimeRangeFilter } from './TimeRangeFilter';

type Props = {
  filters: FilterState;
  authorsData: Author[];
  parameters: Location;
  tagsData: Tag[];
  timeRange: TimeRangeType | null;
  timeRangeData: number[][];
  applyFilters: () => void;
  applySingleFilter: (value: string, filter: FilterType | 'timeRange') => void;
  getAuthorsAndTimeRangeData: () => void;
  resetFilters: () => void;
  toggleFilter: (value: string, filter: FilterType) => void;
  setTimeRange: (value: string | null) => void;
  updateFiltersFromURL: () => void;
};

type FiltersPanelProps = {
  authorsData: Author[];
  filters: FilterState;
  project: string;
  resource: string;
  selectedFiltersCount: number;
  tagsData: Tag[];
  timeRange: TimeRangeType | null;
  timeRangeData: number[][];
  setTimeRange: (value: string | null) => void;
  onApplyFilter: (value: string, filter: FilterType | 'timeRange') => void;
  onApplyFilters: () => void;
  onResetFilters: () => void;
  onToggleFilter: (
    value: string,
    filter: FilterType,
    event?: React.MouseEvent,
  ) => void;
  onDiscard: () => void;
};

const StatusFilter = ({
  onSelect,
  onToggle,
  selected,
  stats,
  status,
}: {
  onSelect: () => void;
  onToggle: () => void;
  selected: boolean;
  stats: Stats;
  status: (typeof FILTERS_STATUS)[number];
}) => (
  <li
    className={classNames(
      status.slug,
      selected && status.slug !== 'all' && 'selected',
    )}
    onClick={onSelect}
  >
    <span
      className='status fa'
      onClick={(ev) => {
        ev.stopPropagation();
        onToggle();
      }}
    ></span>
    <Localized id={`search-FiltersPanel--status-name-${status.slug}`}>
      <span className='title'>{status.name}</span>
    </Localized>
    <span className='count'>
      {asLocaleString(stats['stat' in status ? status.stat : status.slug])}
    </span>
  </li>
);

const TagFilter = ({
  onSelect,
  selected,
  tag: { name, priority, slug },
}: {
  onSelect: () => void;
  selected: boolean;
  tag: Tag;
}) => (
  <li
    className={classNames('tag', slug, selected && 'selected')}
    onClick={onSelect}
  >
    <span className='status fa' onClick={onSelect}></span>
    <span className='title'>{name}</span>
    <span className='priority'>
      {[1, 2, 3, 4, 5].map((index) => (
        <span
          className={classNames('fa', 'fa-star', index <= priority && 'active')}
          key={index}
        ></span>
      ))}
    </span>
  </li>
);

const ExtraFilter = ({
  extra: { name, slug },
  onSelect,
  onToggle,
  selected,
}: {
  extra: (typeof FILTERS_EXTRA)[number];
  onSelect: () => void;
  onToggle: () => void;
  selected: boolean;
}) => (
  <li className={classNames(slug, selected && 'selected')} onClick={onSelect}>
    <span
      className='status fa'
      onClick={(ev) => {
        ev.stopPropagation();
        onToggle();
      }}
    ></span>
    <Localized id={`search-FiltersPanel--extra-name-${slug}`}>
      <span className='title'>{name}</span>
    </Localized>
  </li>
);

const AuthorFilter = ({
  author: { display_name, gravatar_url, role, translation_count },
  onSelect,
  onToggle,
  selected,
}: {
  author: Author;
  onSelect: () => void;
  onToggle: () => void;
  selected: boolean;
}) => (
  <li
    className={classNames('author', selected && 'selected')}
    onClick={onSelect}
  >
    <figure>
      <span className='sel'>
        <span
          className='status fa'
          onClick={(ev) => {
            ev.stopPropagation();
            onToggle();
          }}
        ></span>
        <img
          alt=''
          className='rounded'
          src={gravatar_url}
          width='44'
          height='44'
        />
      </span>
      <figcaption>
        <p className='name'>{display_name}</p>
        <p className='role'>{role}</p>
      </figcaption>
      <span className='count'>{asLocaleString(translation_count)}</span>
    </figure>
  </li>
);

const FilterToolbar = ({
  count,
  onApply,
  onReset,
}: {
  count: number;
  onApply: () => void;
  onReset: () => void;
}) => (
  <div className='toolbar clearfix'>
    <Localized
      id='search-FiltersPanel--clear-selection'
      attrs={{ title: true }}
      elems={{
        glyph: <i className='fa fa-times fa-lg' />,
      }}
    >
      <button
        title='Uncheck selected filters'
        onClick={onReset}
        className='clear-selection'
      >
        {'<glyph></glyph> CLEAR'}
      </button>
    </Localized>
    <Localized
      id='search-FiltersPanel--apply-filters'
      attrs={{ title: true }}
      elems={{
        glyph: <i className='fa fa-check fa-lg' />,
        stress: <span className='applied-count' />,
      }}
      vars={{ count }}
    >
      <button
        title='Apply Selected Filters'
        onClick={onApply}
        className='apply-selected'
      >
        {'<glyph></glyph>APPLY <stress>{ $count }</stress> FILTERS'}
      </button>
    </Localized>
  </div>
);

export function FiltersPanelDialog({
  authorsData,
  filters: { authors, extras, statuses, tags },
  project,
  resource,
  selectedFiltersCount,
  tagsData,
  timeRange,
  timeRangeData,
  setTimeRange,
  onApplyFilter,
  onApplyFilters,
  onResetFilters,
  onToggleFilter,
  onDiscard,
}: FiltersPanelProps): React.ReactElement<'div'> {
  const stats = useStats();
  const ref = React.useRef(null);
  useOnDiscard(ref, onDiscard);

  return (
    <div className='menu' ref={ref}>
      <ul>
        <Localized id='search-FiltersPanel--heading-status'>
          <li className='horizontal-separator'>TRANSLATION STATUS</li>
        </Localized>

        {FILTERS_STATUS.map((status, i) => (
          <StatusFilter
            key={i}
            onSelect={() => onApplyFilter(status.slug, 'statuses')}
            onToggle={() => onToggleFilter(status.slug, 'statuses')}
            selected={statuses.includes(status.slug)}
            stats={stats}
            status={status}
          />
        ))}

        {tagsData.length > 0 && resource === 'all-resources' ? (
          <>
            <Localized id='search-FiltersPanel--heading-tags'>
              <li className='horizontal-separator'>TAGS</li>
            </Localized>

            {tagsData.map((tag, i) => (
              <TagFilter
                key={i}
                onSelect={() => onApplyFilter(tag.slug, 'tags')}
                selected={tags.includes(tag.slug)}
                tag={tag}
              />
            ))}
          </>
        ) : null}

        <Localized id='search-FiltersPanel--heading-extra'>
          <li className='horizontal-separator'>EXTRA FILTERS</li>
        </Localized>

        {FILTERS_EXTRA.map((extra, i) => (
          <ExtraFilter
            extra={extra}
            key={i}
            onSelect={() => onApplyFilter(extra.slug, 'extras')}
            onToggle={() => onToggleFilter(extra.slug, 'extras')}
            selected={extras.includes(extra.slug)}
          />
        ))}

        <TimeRangeFilter
          project={project}
          timeRange={timeRange}
          timeRangeData={timeRangeData}
          applySingleFilter={onApplyFilter}
          setTimeRange={setTimeRange}
        />

        {authorsData.length > 0 && project !== 'all-projects' ? (
          <>
            <Localized id='search-FiltersPanel--heading-authors'>
              <li className='horizontal-separator'>TRANSLATION AUTHORS</li>
            </Localized>

            {authorsData.map((author, i) => (
              <AuthorFilter
                author={author}
                key={i}
                onSelect={() => onApplyFilter(author.email, 'authors')}
                onToggle={() => onToggleFilter(author.email, 'authors')}
                selected={authors.includes(author.email)}
              />
            ))}
          </>
        ) : null}
      </ul>

      {selectedFiltersCount > 0 ? (
        <FilterToolbar
          count={selectedFiltersCount}
          onApply={onApplyFilters}
          onReset={onResetFilters}
        />
      ) : null}
    </div>
  );
}

/**
 * Shows a list of filters, used to filter the list of entities.
 *
 * Changes to the filters will be reflected in the URL.
 */
export function FiltersPanel({
  filters,
  tagsData,
  timeRangeData,
  authorsData,
  parameters,
  timeRange,
  applyFilters,
  applySingleFilter,
  getAuthorsAndTimeRangeData,
  resetFilters,
  toggleFilter,
  updateFiltersFromURL,
  setTimeRange: setTimeRange,
}: Props): React.ReactElement<'div'> | null {
  const [visible, setVisible] = useState(false);

  const toggleVisible = useCallback(() => {
    setVisible((prev) => !prev);
    updateFiltersFromURL();
  }, [updateFiltersFromURL]);

  const handleDiscard = useCallback(() => {
    setVisible(false);
    updateFiltersFromURL();
  }, [updateFiltersFromURL]);

  useEffect(() => {
    if (visible && parameters.project !== 'all-projects') {
      getAuthorsAndTimeRangeData();
    }
  }, [getAuthorsAndTimeRangeData, parameters.project, visible]);

  const handleToggleFilter = useCallback(
    (value: string, filter: FilterType, ev?: React.MouseEvent) => {
      if (value !== 'all') {
        ev?.stopPropagation();
        toggleFilter(value, filter);
      }
    },
    [toggleFilter],
  );

  const handleApplyFilter = useCallback(
    (value: string, filter: FilterType | 'timeRange') => {
      toggleVisible();
      applySingleFilter(value, filter);
    },
    [applySingleFilter],
  );

  const handleApplyFilters = useCallback(() => {
    setVisible(false);
    applyFilters();
  }, [applyFilters]);

  const { filterIcon, selectedCount } = useMemo(() => {
    const { authors, extras, statuses, tags } = filters;
    let selectedCount = 0;
    let filterIcon: string | null = null;
    for (const [source, data, field] of [
      [statuses, FILTERS_STATUS, 'slug'],
      [extras, FILTERS_EXTRA, 'slug'],
      [tags, tagsData, 'slug'],
      [authors, authorsData, 'email'],
    ] as [string[], Record<string, unknown>[], string][]) {
      for (const selected of source) {
        selectedCount += 1;
        filterIcon ??= data.some((f) => f[field] === selected)
          ? selected
          : null;
      }
    }
    if (timeRange) {
      selectedCount += 1;
      filterIcon ??= 'time-range';
    }
    filterIcon ??= parameters.list ? 'list' : 'all';
    return { filterIcon, selectedCount };
  }, [filters, parameters.list, tagsData, authorsData]);

  return (
    <div className='filters-panel'>
      <div
        className={`visibility-switch ${filterIcon}`}
        onClick={toggleVisible}
      >
        <span className='status fa'></span>
      </div>
      {visible ? (
        <FiltersPanelDialog
          authorsData={authorsData}
          filters={filters}
          project={parameters.project}
          resource={parameters.resource}
          selectedFiltersCount={selectedCount}
          tagsData={tagsData}
          timeRange={timeRange}
          timeRangeData={timeRangeData}
          setTimeRange={setTimeRange}
          onApplyFilter={handleApplyFilter}
          onApplyFilters={handleApplyFilters}
          onDiscard={handleDiscard}
          onResetFilters={resetFilters}
          onToggleFilter={handleToggleFilter}
        />
      ) : null}
    </div>
  );
}

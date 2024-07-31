import { Localized } from '@fluent/react';
import React, { useCallback, useMemo, useState } from 'react';
import classNames from 'classnames';
import { FILTERS_SEARCH } from '../constants';
import type { FilterState, FilterType } from './SearchBox';

import { useOnDiscard } from '~/utils';

import './SearchPanel.css';

type Props = {
  filters: FilterState;
  resetFilters: () => void;
  applyFilters: () => void;
  applySingleFilter: (value: string, filter: FilterType | 'timeRange') => void;
  toggleFilter: (value: string, filter: FilterType) => void;
};

type SearchPanelProps = {
  filters: FilterState;
  selectedFiltersCount: number;
  onResetFilters: () => void;
  onApplyFilters: () => void;
  onApplyFilter: (value: string, filter: FilterType | 'timeRange') => void;
  onToggleFilter: (
    value: string,
    filter: FilterType,
    event?: React.MouseEvent,
  ) => void;
  onDiscard: () => void;
};

const SearchFilter = ({
  filter: { name },
  selected,
  onSelect,
  onToggle,
}: {
  filter: (typeof FILTERS_SEARCH)[number];
  selected: boolean;
  onSelect: () => void;
  onToggle: () => void;
}) => {
  return (
    <li
      className={classNames('check-box', selected && 'enabled')}
      onClick={onSelect}
    >
      <i
        className='fa fa-w'
        onClick={(ev) => {
          ev.stopPropagation();
          onToggle();
        }}
      ></i>
      <span className='label'>{name}</span>
    </li>
  );
};

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

export function SearchPanelDialog({
  filters,
  selectedFiltersCount,
  onResetFilters,
  onApplyFilter,
  onApplyFilters,
  onToggleFilter,
  onDiscard,
}: SearchPanelProps): React.ReactElement<'div'> {
  const ref = React.useRef(null);
  useOnDiscard(ref, onDiscard);

  return (
    <div className='menu' ref={ref}>
      <ul>
        <li className='title'>SEARCH OPTIONS</li>

        {FILTERS_SEARCH.map((search, i) => (
          <SearchFilter
            onSelect={() => onApplyFilter(search.slug, 'search_filters')}
            onToggle={() => onToggleFilter(search.slug, 'search_filters')}
            filter={search}
            key={i}
            selected={filters.search_filters.includes(search.slug)}
          />
        ))}
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

export function SearchPanel({
  filters,
  resetFilters,
  applyFilters,
  applySingleFilter,
  toggleFilter,
}: Props): React.ReactElement<'div'> | null {
  const [visible, setVisible] = useState(false);

  const toggleVisible = useCallback(() => {
    setVisible((prev) => !prev);
  }, []);

  const handleDiscard = useCallback(() => {
    setVisible(false);
  }, []);

  const handleToggleFilter = useCallback(
    (value: string, filter: FilterType, ev?: React.MouseEvent) => {
      if (value !== 'all') {
        ev?.stopPropagation();
        toggleFilter(value, filter);
      }
    },
    [toggleFilter],
  );

  const handleApplyFilters = useCallback(() => {
    setVisible(false);
    applyFilters();
  }, [applyFilters]);

  const { selectedCount } = useMemo(() => {
    const { search_filters } = filters;
    let selectedCount = 0;

    search_filters.forEach(() => {
      selectedCount += 1;
    });

    return { selectedCount };
  }, [filters]);

  return (
    <div className='search-panel'>
      <div className='visibility-switch' onClick={toggleVisible}>
        <span className='fa fa-search'></span>
      </div>
      {visible ? (
        <SearchPanelDialog
          filters={filters}
          selectedFiltersCount={selectedCount}
          onResetFilters={resetFilters}
          onApplyFilter={applySingleFilter}
          onApplyFilters={handleApplyFilters}
          onToggleFilter={handleToggleFilter}
          onDiscard={handleDiscard}
        />
      ) : null}
    </div>
  );
}

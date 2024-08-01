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
      onClick={(ev) => {
        ev.stopPropagation();
        onToggle();
      }}
    >
      <i className='fa fa-w'></i>
      <span className='label'>{name}</span>
    </li>
  );
};

const FilterToolbar = ({ onApply }: { onApply: () => void }) => (
  <div className='toolbar clearfix'>
    <button
      title='Apply Selected Filters'
      onClick={onApply}
      className='apply-selected'
    >
      {'SEARCH'}
    </button>
  </div>
);

export function SearchPanelDialog({
  filters,
  selectedFiltersCount,
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
        <FilterToolbar onApply={onApplyFilters} />
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

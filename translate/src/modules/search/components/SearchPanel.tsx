import React, { useCallback, useState } from 'react';
import classNames from 'classnames';
import { SEARCH_OPTIONS } from '../constants';
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
  filter: (typeof SEARCH_OPTIONS)[number];
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

export function SearchPanelDialog({
  filters,
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

        {SEARCH_OPTIONS.map((search, i) => (
          <SearchFilter
            onSelect={() => onApplyFilter(search.slug, 'search_identifiers')}
            onToggle={() => onToggleFilter(search.slug, 'search_identifiers')}
            filter={search}
            key={i}
            selected={filters.search_identifiers.includes(search.slug)}
          />
        ))}
      </ul>

      <button
        title='Apply Selected Filters'
        onClick={onApplyFilters}
        className='search-button'
      >
        {' '}
        {'SEARCH'}
      </button>
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

  return (
    <div className='search-panel'>
      <div className='visibility-switch' onClick={toggleVisible}>
        <span className='fa fa-search'></span>
      </div>
      {visible ? (
        <SearchPanelDialog
          filters={filters}
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

import React, { useCallback, useState } from 'react';
import { Localized } from '@fluent/react';
import classNames from 'classnames';
import { SEARCH_OPTIONS } from '../constants';
import type { FilterState, FilterType } from './SearchBox';

import { useOnDiscard } from '~/utils';

import './SearchPanel.css';

type Props = {
  filters: FilterState;
  applyFilters: () => void;
  toggleFilter: (value: string, filter: FilterType) => void;
};

type SearchPanelProps = {
  filters: FilterState;
  onApplyFilters: () => void;
  onToggleFilter: (
    value: string,
    filter: FilterType,
    event?: React.MouseEvent,
  ) => void;
  onDiscard: () => void;
};

const SearchFilter = ({
  filter: { name, slug },
  selected,
  onToggle,
}: {
  filter: (typeof SEARCH_OPTIONS)[number];
  selected: boolean;
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
      <Localized id={`search-SearchOptionsPanel--option-name-${slug}`}>
        <span className='label'>{name}</span>
      </Localized>
    </li>
  );
};

export function SearchPanelDialog({
  filters,
  onApplyFilters,
  onToggleFilter,
  onDiscard,
}: SearchPanelProps): React.ReactElement<'div'> {
  const ref = React.useRef(null);
  useOnDiscard(ref, onDiscard);

  return (
    <div className='menu' ref={ref}>
      <Localized id='search-SearchOptionsPanel--heading'>
        <header className='title'>SEARCH OPTIONS</header>
      </Localized>
      <ul>
        {SEARCH_OPTIONS.map((search, i) => (
          <SearchFilter
            onToggle={() => onToggleFilter(search.slug, 'search_identifiers')}
            filter={search}
            key={i}
            selected={filters.search_identifiers.includes(search.slug)}
          />
        ))}
      </ul>

      <Localized id='search-SearchOptionsPanel--apply-options'>
        <button
          title='Apply Selected Search Options'
          onClick={onApplyFilters}
          className='search-button'
        >
          {'APPLY SEARCH OPTIONS'}
        </button>
      </Localized>
    </div>
  );
}

export function SearchPanel({
  filters,
  applyFilters,
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
          onApplyFilters={handleApplyFilters}
          onToggleFilter={handleToggleFilter}
          onDiscard={handleDiscard}
        />
      ) : null}
    </div>
  );
}

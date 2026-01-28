import React, { useCallback, useState, useEffect } from 'react';
import { Localized } from '@fluent/react';
import classNames from 'classnames';
import { SEARCH_OPTIONS } from '../constants';
import type { SearchState, SearchType } from './SearchBox';

import { useOnDiscard } from '~/utils';

import './SearchPanel.css';

type Props = {
  searchOptions: SearchState;
  applyOptions: () => void;
  toggleOption: (searchOption: SearchType) => void;
};

type SearchPanelProps = {
  selectedSearchOptions: SearchState;
  onApplyOptions: () => void;
  onToggleOption: (searchOption: SearchType, event?: React.MouseEvent) => void;
  onDiscard: () => void;
};

const SearchOption = ({
  searchOption: { name, slug },
  selected,
  onToggle,
}: {
  searchOption: (typeof SEARCH_OPTIONS)[number];
  selected: boolean;
  onToggle: () => void;
}) => {
  return (
    <li
      className={classNames(`check-box ${slug}`, selected && 'enabled')}
      onClick={(ev) => {
        ev.stopPropagation();
        onToggle();
      }}
    >
      <i className='fas'></i>
      <Localized
        id={`search-SearchPanel--option-name-${slug.replace(/_/g, '-')}`}
      >
        <span className='label'>{name}</span>
      </Localized>
    </li>
  );
};

export function SearchPanelDialog({
  selectedSearchOptions,
  onApplyOptions,
  onToggleOption,
  onDiscard,
}: SearchPanelProps): React.ReactElement<'div'> {
  const ref = React.useRef(null);
  useOnDiscard(ref, onDiscard);

  return (
    <div className='menu' ref={ref} data-testid='search-panel-dialog'>
      <Localized id='search-SearchPanel--heading'>
        <header className='title'>SEARCH OPTIONS</header>
      </Localized>
      <ul>
        {SEARCH_OPTIONS.map((search, i) => (
          <SearchOption
            onToggle={() => onToggleOption(search.slug)}
            searchOption={search}
            key={i}
            selected={selectedSearchOptions[search.slug] ?? false}
          />
        ))}
      </ul>

      <Localized id='search-SearchPanel--apply-search-options'>
        <button
          title='Apply Selected Search Options'
          onClick={onApplyOptions}
          className='search-button'
        >
          {'APPLY SEARCH OPTIONS'}
        </button>
      </Localized>
    </div>
  );
}

export function SearchPanel({
  searchOptions,
  applyOptions,
  toggleOption,
}: Props): React.ReactElement<'div'> | null {
  const [visible, setVisible] = useState(false);
  // selectedSearchOptions maintains the visual state of the checkboxes, even on discard
  const [selectedSearchOptions, setSelectedSearchOptions] =
    useState(searchOptions);

  useEffect(() => {
    if (visible) {
      setSelectedSearchOptions(searchOptions);
    }
  }, [visible, searchOptions]);

  const toggleVisible = useCallback(() => {
    setVisible((prev) => !prev);
  }, []);

  const handleDiscard = useCallback(() => {
    setVisible(false);
  }, []);

  const handleToggleOption = useCallback(
    (searchOption: SearchType, ev?: React.MouseEvent) => {
      ev?.stopPropagation();
      setSelectedSearchOptions((prev) => ({
        ...prev,
        [searchOption]: !prev[searchOption],
      }));
      toggleOption(searchOption);
    },
    [toggleOption],
  );

  const handleApplyOptions = useCallback(() => {
    setVisible(false);
    applyOptions();
  }, [applyOptions]);

  return (
    <div className='search-panel'>
      <div className='visibility-switch' onClick={toggleVisible}>
        <span className='fa-stack'>
          <i className='fas fa-search fa-stack-2x'></i>
          <i className='fas fa-caret-down fa-stack-1x'></i>
        </span>
      </div>
      {visible ? (
        <SearchPanelDialog
          selectedSearchOptions={selectedSearchOptions}
          onApplyOptions={handleApplyOptions}
          onToggleOption={handleToggleOption}
          onDiscard={handleDiscard}
        />
      ) : null}
    </div>
  );
}

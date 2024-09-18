import React, { useCallback, useState } from 'react';
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
  updateOptionsFromURL: () => void;
};

type SearchPanelProps = {
  searchOptions: SearchState;
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
  // Find the first option that doesn't have "Match" in the name, and apply top margin for visual seperation
  const seperator = SEARCH_OPTIONS.find(
    (option) => !option.name.includes('Match'),
  )?.name;

  return (
    <li
      className={classNames(
        'check-box',
        selected && 'enabled',
        name === seperator && 'option-seperator',
      )}
      onClick={(ev) => {
        ev.stopPropagation();
        onToggle();
      }}
    >
      <i className='fa fa-w'></i>
      <Localized id={`search-SearchPanel--option-name-${slug}`}>
        <span className='label'>{name}</span>
      </Localized>
    </li>
  );
};

export function SearchPanelDialog({
  searchOptions,
  onApplyOptions,
  onToggleOption,
  onDiscard,
}: SearchPanelProps): React.ReactElement<'div'> {
  const ref = React.useRef(null);
  useOnDiscard(ref, onDiscard);

  return (
    <div className='menu' ref={ref}>
      <Localized id='search-SearchPanel--heading'>
        <header className='title'>SEARCH OPTIONS</header>
      </Localized>
      <ul>
        {SEARCH_OPTIONS.map((search, i) => (
          <SearchOption
            onToggle={() => onToggleOption(search.slug)}
            searchOption={search}
            key={i}
            selected={searchOptions[search.slug] ?? false}
          />
        ))}
      </ul>

      <Localized id='search-SearchPanel--apply-searchOptions'>
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
  updateOptionsFromURL,
}: Props): React.ReactElement<'div'> | null {
  const [visible, setVisible] = useState(false);

  const toggleVisible = useCallback(() => {
    setVisible((prev) => !prev);
    updateOptionsFromURL();
  }, [updateOptionsFromURL]);

  const handleDiscard = useCallback(() => {
    setVisible(false);
    updateOptionsFromURL();
  }, [updateOptionsFromURL]);

  const handleToggleOption = useCallback(
    (searchOption: SearchType, ev?: React.MouseEvent) => {
      ev?.stopPropagation();
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
        <span className='fa fa-search'></span>
      </div>
      {visible ? (
        <SearchPanelDialog
          searchOptions={searchOptions}
          onApplyOptions={handleApplyOptions}
          onToggleOption={handleToggleOption}
          onDiscard={handleDiscard}
        />
      ) : null}
    </div>
  );
}

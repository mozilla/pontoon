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
  restoreDefaults: () => void;
  toggleOption: (searchOption: SearchType) => void;
};

type SearchPanelProps = {
  searchOptions: SearchState;
  onApplyOptions: () => void;
  onToggleOption: (searchOption: SearchType, event?: React.MouseEvent) => void;
  onRestoreDefaults: () => void;
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
      className={classNames('check-box', slug, selected && 'enabled')}
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

const SEPARATOR_AFTER = new Set([
  'search_match_whole_word',
  'search_exclude_source_strings',
]);

export function SearchPanelDialog({
  searchOptions,
  onApplyOptions,
  onToggleOption,
  onRestoreDefaults,
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
          <React.Fragment key={i}>
            <SearchOption
              onToggle={() => onToggleOption(search.slug)}
              searchOption={search}
              selected={searchOptions[search.slug] ?? false}
            />
            {SEPARATOR_AFTER.has(search.slug) && (
              <li className='separator' role='separator' />
            )}
          </React.Fragment>
        ))}
        <li
          className='action-item'
          onClick={(ev) => {
            ev.stopPropagation();
            onRestoreDefaults();
          }}
        >
          <Localized id='search-SearchPanel--restore-default-options'>
            <span>{'Restore default options'}</span>
          </Localized>
        </li>
        <li className='action-item'>
          <Localized id='search-SearchPanel--change-default-search-settings'>
            <a href='/settings/#search'>{'Change default search settings'}</a>
          </Localized>
        </li>
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
  restoreDefaults,
  toggleOption,
}: Props): React.ReactElement<'div'> | null {
  const [visible, setVisible] = useState(false);

  const toggleVisible = useCallback(() => {
    setVisible((prev) => !prev);
  }, []);

  const handleDiscard = useCallback(() => {
    setVisible(false);
  }, []);

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
      <div className='visibility-switch' role='button' onClick={toggleVisible}>
        <span className='fa-stack'>
          <i className='fas fa-search fa-stack-2x'></i>
          <i className='fas fa-caret-down fa-stack-1x'></i>
        </span>
      </div>
      {visible ? (
        <SearchPanelDialog
          searchOptions={searchOptions}
          onApplyOptions={handleApplyOptions}
          onToggleOption={handleToggleOption}
          onRestoreDefaults={restoreDefaults}
          onDiscard={handleDiscard}
        />
      ) : null}
    </div>
  );
}

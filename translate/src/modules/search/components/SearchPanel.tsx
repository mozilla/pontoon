import React, { useCallback, useState } from 'react';
import { Localized } from '@fluent/react';
import classNames from 'classnames';
import { SEARCH_OPTIONS } from '../constants';
import type { SearchState, SearchType } from './SearchBox';

import { useOnDiscard } from '~/utils';

import './SearchPanel.css';

type Props = {
  options: SearchState;
  applyOptions: () => void;
  toggleOption: (value: string, filter: SearchType) => void;
  updateOptionsFromURL: () => void;
};

type SearchPanelProps = {
  options: SearchState;
  onApplyOptions: () => void;
  onToggleOption: (
    value: string,
    option: SearchType,
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
      <Localized id={`search-SearchPanel--option-name-${slug}`}>
        <span className='label'>{name}</span>
      </Localized>
    </li>
  );
};

export function SearchPanelDialog({
  options,
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
          <SearchFilter
            onToggle={() => onToggleOption(search.slug, 'search_identifiers')}
            filter={search}
            key={i}
            selected={options.search_identifiers.includes(search.slug)}
          />
        ))}
      </ul>

      <Localized id='search-SearchPanel--apply-options'>
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
  options,
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
    (value: string, option: SearchType, ev?: React.MouseEvent) => {
      if (value !== 'all') {
        ev?.stopPropagation();
        toggleOption(value, option);
      }
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
          options={options}
          onApplyOptions={handleApplyOptions}
          onToggleOption={handleToggleOption}
          onDiscard={handleDiscard}
        />
      ) : null}
    </div>
  );
}

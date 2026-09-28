import { Localized } from '@fluent/react';
import React, { useContext, useState } from 'react';

import { logUXAction } from '~/api/uxaction';
import { Locale } from '~/context/Locale';

type Props = {
  /** The characteristic currently applied, or '' when showing the original. */
  selectedOption: string;
  onSelect: (characteristic: string) => Promise<void> | void;
  onRestore: () => void;
};

/**
 * The "Refine using AI" dropdown.
 *
 * Always the last item of a suggestion's source list, never attached to one of
 * the source labels: it acts on the suggestion, and a suggestion can be
 * assembled from several sources with no one of them owning it.
 */
export function AIRefine({
  selectedOption,
  onSelect,
  onRestore,
}: Props): React.ReactElement<'li'> {
  const [isDropdownOpen, setDropdownOpen] = useState(false);
  const locale = useContext(Locale);

  const toggleDropdown = (ev: React.MouseEvent) => {
    ev.stopPropagation();
    setDropdownOpen((isDropdownOpen) => !isDropdownOpen);
  };

  const handleOptionClick = async (ev: React.MouseEvent<HTMLLIElement>) => {
    ev.stopPropagation();
    const characteristic = ev.currentTarget.dataset['characteristic'] as string;

    if (characteristic === 'original') {
      onRestore();
    } else {
      await onSelect(characteristic);
      logUXAction('LLM Dropdown Select', 'LLM Feature Adoption', {
        optionSelected: characteristic,
        localeCode: locale.code,
      });
    }
    setDropdownOpen(false);
  };

  return (
    <li className='ai-refine'>
      <Localized id='machinery-AIRefine--selector'>
        <span
          className='selector'
          onClick={toggleDropdown}
          title='Refine using AI'
        >
          {selectedOption ? (
            <Localized id={`machinery-AIRefine--option-${selectedOption}`}>
              <span className='selected-option'>{selectedOption}</span>
            </Localized>
          ) : (
            <span className='selected-option'>{selectedOption}</span>
          )}

          <button
            className='dropdown-toggle'
            aria-haspopup='true'
            aria-expanded={isDropdownOpen}
          >
            <Localized id='machinery-AIRefine--dropdown-title'>
              <span className='dropdown-title'>AI</span>
            </Localized>
            <i className='fas fa-caret-down'></i>
          </button>
        </span>
      </Localized>
      {isDropdownOpen && (
        <ul className='dropdown-menu'>
          <Localized id='machinery-AIRefine--option-rephrase'>
            <li
              data-characteristic='rephrased'
              onClick={handleOptionClick}
              title=''
            >
              REPHRASE
            </li>
          </Localized>
          <Localized id='machinery-AIRefine--option-make-formal'>
            <li
              data-characteristic='formal'
              onClick={handleOptionClick}
              title=''
            >
              MAKE FORMAL
            </li>
          </Localized>
          <Localized id='machinery-AIRefine--option-make-informal'>
            <li
              data-characteristic='informal'
              onClick={handleOptionClick}
              title=''
            >
              MAKE INFORMAL
            </li>
          </Localized>
          {selectedOption && (
            <>
              <li className='horizontal-separator'></li>
              <Localized id='machinery-AIRefine--option-show-original'>
                <li
                  data-characteristic='original'
                  onClick={handleOptionClick}
                  title=''
                >
                  SHOW ORIGINAL
                </li>
              </Localized>
            </>
          )}
        </ul>
      )}
    </li>
  );
}

import React, { useState, useRef, useContext } from 'react';
import { Localized } from '@fluent/react';
import type { MachineryTranslation } from '~/api/machinery';
import { Locale } from '~/context/Locale';
import { logUXAction } from '~/api/uxaction';
import { useLLMTranslation } from '~/context/TranslationContext';

type Props = {
  translation: MachineryTranslation;
};

/**
 * Show the translation source from Google Translate.
 */

export function GoogleTranslation({
  translation,
}: Props): React.ReactElement<'li'> {
  const [isDropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLLIElement>(null);
  const locale = useContext(Locale);

  const { transformLLMTranslation, selectedOption } =
    useLLMTranslation(translation);

  const toggleDropdown = (ev: React.MouseEvent) => {
    ev.stopPropagation();
    setDropdownOpen((isDropdownOpen) => !isDropdownOpen);
  };

  const handleOptionClick = async (ev: React.MouseEvent<HTMLLIElement>) => {
    ev.stopPropagation();
    const target = ev.currentTarget;
    const characteristic = target.dataset['characteristic'];

    if (characteristic) {
      setDropdownOpen(false);
      await transformLLMTranslation(translation, characteristic, locale.name);

      logUXAction('LLM Dropdown Select', 'LLM Feature Adoption', {
        optionSelected: characteristic,
        targetLanguage: locale.name,
      });
    }
  };

  let selectedOptionText: string;
  switch (selectedOption) {
    case 'alternative':
      selectedOptionText = 'REPHRASED';
      break;
    case 'formal':
      selectedOptionText = 'FORMAL';
      break;
    case 'informal':
      selectedOptionText = 'INFORMAL';
      break;
    default:
      selectedOptionText = '';
  }

  return (
    <li ref={dropdownRef} className='google-translation'>
      <Localized id='machinery-GoogleTranslation--translation-source'>
        <span
          className='translation-source'
          title='Toggle dropdown'
          onClick={toggleDropdown}
        >
          <span>GOOGLE TRANSLATE</span>
        </span>
      </Localized>
      <span className='selected-option'>{selectedOptionText}</span>
      <button
        onClick={toggleDropdown}
        className='dropdown-toggle'
        aria-haspopup='true'
        aria-expanded={isDropdownOpen}
      >
        <i className='fa fa-caret-down'></i>
      </button>
      {isDropdownOpen && (
        <ul className='dropdown-menu'>
          <Localized id='machinery-GoogleTranslation--option-rephrase'>
            <li data-characteristic='alternative' onClick={handleOptionClick}>
              REPHRASE
            </li>
          </Localized>
          <Localized id='machinery-GoogleTranslation--option-make-formal'>
            <li data-characteristic='formal' onClick={handleOptionClick}>
              MAKE FORMAL
            </li>
          </Localized>
          <Localized id='machinery-GoogleTranslation--option-make-informal'>
            <li data-characteristic='informal' onClick={handleOptionClick}>
              MAKE INFORMAL
            </li>
          </Localized>
          <li className='horizontal-separator'></li>
          <Localized id='machinery-GoogleTranslation--option-show-original'>
            <li data-characteristic='original' onClick={handleOptionClick}>
              SHOW ORIGINAL
            </li>
          </Localized>
        </ul>
      )}
    </li>
  );
}

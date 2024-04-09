import React, { useState, useRef, useContext, useEffect } from 'react';
import { Localized } from '@fluent/react';
import type { MachineryTranslation } from '~/api/machinery';
import { fetchGPTTransform } from '~/api/machinery';
import { Locale } from '~/context/Locale';
import { logUXAction } from '~/api/uxaction';

type Props = {
  translation: MachineryTranslation;
  onLLMTranslationChange: (llmTranslation: string) => void;
};

/**
 * Show the translation source from Google Translate.
 */

export function GoogleTranslation({
  translation,
  onLLMTranslationChange,
}: Props): React.ReactElement<'li'> {
  const [isDropdownOpen, setDropdownOpen] = useState(false);
  const [selectedOption, setSelectedOption] = useState('');
  const [showOriginalOption, setShowOriginalOption] = useState(false);
  const [currentTranslation, setCurrentTranslation] = useState(
    translation.translation,
  );
  const dropdownRef = useRef<HTMLLIElement>(null);
  const locale = useContext(Locale);
  const [llmTranslation, setLLMTranslation] = useState('');

  const toggleDropdown = (ev: React.MouseEvent) => {
    ev.stopPropagation();
    setDropdownOpen((isDropdownOpen) => !isDropdownOpen);
  };

  useEffect(() => {
    // Whenever llmTranslation changes, communicate this change to the parent component
    onLLMTranslationChange(llmTranslation);
  }, [llmTranslation]);

  const handleTransformation = async (characteristic: string) => {
    // Only fetch transformation if not reverting to original
    if (characteristic !== 'original') {
      const machineryTranslations = await fetchGPTTransform(
        translation.original,
        currentTranslation,
        characteristic,
        locale.name,
      );

      if (machineryTranslations.length > 0) {
        setCurrentTranslation(machineryTranslations[0].translation);
        setLLMTranslation(machineryTranslations[0].translation);
        setShowOriginalOption(true);
      }
    } else {
      setCurrentTranslation(translation.translation);
      setLLMTranslation('');
      setSelectedOption('');
      setShowOriginalOption(false);
    }
  };

  const handleOptionClick = (ev: React.MouseEvent<HTMLLIElement>) => {
    ev.stopPropagation();
    const target = ev.currentTarget;
    const characteristic = target.getAttribute('data-characteristic');

    if (characteristic) {
      let displayText = '';

      switch (characteristic) {
        case 'alternative':
          displayText = 'REPHRASED';
          break;
        case 'formal':
          displayText = 'FORMAL';
          break;
        case 'informal':
          displayText = 'INFORMAL';
          break;
        case 'original':
          displayText = '';
          break;
        default:
          break;
      }
      setSelectedOption(displayText);
      setDropdownOpen(false);

      const trackllmTranslation = target.innerText;
      onLLMTranslationChange(trackllmTranslation);

      logUXAction('LLM Dropdown Select', 'LLM Feature Adoption', {
        optionSelected: trackllmTranslation,
        targetLanguage: locale.name,
      });

      handleTransformation(characteristic);
    }
  };

  return (
    <li ref={dropdownRef} className='translation-dropdown-container'>
      <Localized
        id='machinery-GoogleTranslation--visit-google'
        attrs={{ title: true }}
      >
        <span
          className='translation-source'
          title='Toggle dropdown'
          onClick={toggleDropdown}
        >
          <span>GOOGLE TRANSLATE</span>
        </span>
      </Localized>
      <span className='selected-option'>{selectedOption.toUpperCase()}</span>
      <button
        onClick={toggleDropdown}
        className='dropdown-toggle'
        aria-haspopup='true'
        aria-expanded={isDropdownOpen}
      >
        <i className='fa fa-caret-down'></i>
      </button>
      {isDropdownOpen && (
        <ul className='dropdown-menu' style={{ display: 'block' }}>
          <li data-characteristic='alternative' onClick={handleOptionClick}>
            REPHRASE
          </li>
          <li data-characteristic='formal' onClick={handleOptionClick}>
            MAKE FORMAL
          </li>
          <li data-characteristic='informal' onClick={handleOptionClick}>
            MAKE INFORMAL
          </li>
          {showOriginalOption && (
            <li data-characteristic='original' onClick={handleOptionClick}>
              SHOW ORIGINAL
            </li>
          )}
        </ul>
      )}
    </li>
  );
}

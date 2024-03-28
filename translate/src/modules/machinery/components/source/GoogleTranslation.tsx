import React, { useState, useRef, useContext, useEffect } from 'react';
import { Localized } from '@fluent/react';
import type { MachineryTranslation } from '~/api/machinery';
import { fetchGPTTransformation } from '~/api/machinery';
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

  const handleTransformation = async (
    ev: React.MouseEvent,
    characteristic: string,
  ) => {
    ev.stopPropagation();
    try {
      // Only fetch transformation if not reverting to original
      if (characteristic !== 'original') {
        const machineryTranslations = await fetchGPTTransformation(
          translation.original,
          currentTranslation,
          characteristic,
          locale.name,
        );

        if (machineryTranslations.length > 0) {
          const translationWithoutQuotes =
            machineryTranslations[0].translation.replace(
              /^['"](.*)['"]$/,
              '$1',
            );
          setCurrentTranslation(translationWithoutQuotes);
          setLLMTranslation(translationWithoutQuotes);
          setShowOriginalOption(true);
        }
      } else {
        console.log(translation.translation);
        setCurrentTranslation(translation.translation);
        setLLMTranslation('');
        setSelectedOption('');
        setShowOriginalOption(false);
      }
    } catch (error) {
      console.error('Error fetching GPT transformation:', error);
    }
  };

  const handleOptionClick = (ev: React.MouseEvent, option: string) => {
    ev.stopPropagation();
    setSelectedOption(option);
    setDropdownOpen(false);

    let characteristic = '';
    switch (option) {
      case 'Rephrase':
        characteristic = 'alternative';
        setSelectedOption('REPHRASED');
        break;
      case 'Make formal':
        characteristic = 'formal';
        setSelectedOption('FORMAL');
        break;
      case 'Make informal':
        characteristic = 'informal';
        setSelectedOption('INFORMAL');
        break;
      case 'Show original':
        characteristic = 'original'; // Special handling to revert to original
        break;
      default:
        break;
    }

    const trackllmTranslation = option;
    onLLMTranslationChange(trackllmTranslation);

    logUXAction('LLM Dropdown Select', 'LLM Feature Adoption', {
      optionSelected: option,
      targetLanguage: locale.name,
    });

    handleTransformation(ev, characteristic);
  };

  return (
    <li ref={dropdownRef} className='google-translation'>
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
          <li onClick={(ev) => handleOptionClick(ev, 'Rephrase')}>REPHRASE</li>
          <li onClick={(ev) => handleOptionClick(ev, 'Make formal')}>
            MAKE FORMAL
          </li>
          <li onClick={(ev) => handleOptionClick(ev, 'Make informal')}>
            MAKE INFORMAL
          </li>
          {showOriginalOption && (
            <li onClick={(ev) => handleOptionClick(ev, 'Show original')}>
              SHOW ORIGINAL
            </li>
          )}
        </ul>
      )}
    </li>
  );
}

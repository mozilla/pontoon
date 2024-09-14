import React, { useState, useRef, useContext } from 'react';
import { Localized } from '@fluent/react';
import type { MachineryTranslation } from '~/api/machinery';
import { Locale } from '~/context/Locale';
import { logUXAction } from '~/api/uxaction';
import { useLLMTranslation } from '~/context/TranslationContext';

type Props = {
  isOpenAIChatGPTSupported: boolean;
  translation: MachineryTranslation;
};

/**
 * Show the translation source from Google Translate.
 *
 * If OpenAI ChatGPT is supported, this component also handles machine translation
 * refinement using AI.
 */

export function GoogleTranslation({
  isOpenAIChatGPTSupported,
  translation,
}: Props): React.ReactElement<'li'> {
  const [isDropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLLIElement>(null);
  const locale = useContext(Locale);

  const getLLMTranslationState = useLLMTranslation();

  const { transformLLMTranslation, selectedOption, restoreOriginal } =
    getLLMTranslationState(translation);

  const toggleDropdown = (ev: React.MouseEvent) => {
    ev.stopPropagation();
    setDropdownOpen((isDropdownOpen) => !isDropdownOpen);
  };

  const handleOptionClick = async (ev: React.MouseEvent<HTMLLIElement>) => {
    ev.stopPropagation();
    const target = ev.currentTarget;
    const characteristic = target.dataset['characteristic'] as string;

    if (characteristic === 'original') {
      restoreOriginal(translation);
    } else {
      await transformLLMTranslation(translation, characteristic, locale.name);
      logUXAction('LLM Dropdown Select', 'LLM Feature Adoption', {
        optionSelected: characteristic,
        localeCode: locale.code,
      });
    }
    setDropdownOpen(false);
  };

  const title = (
    <Localized id='machinery-GoogleTranslation--translation-source'>
      <span className='translation-source'>GOOGLE TRANSLATE</span>
    </Localized>
  );

  return isOpenAIChatGPTSupported ? (
    <li ref={dropdownRef} className='google-translation'>
      <Localized id='machinery-GoogleTranslation--selector'>
        <span
          className='selector'
          onClick={toggleDropdown}
          title='Refine using AI'
        >
          {title}

          {selectedOption ? (
            <Localized
              id={`machinery-GoogleTranslation--option-${selectedOption}`}
            >
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
            <Localized id='machinery-GoogleTranslation--dropdown-title'>
              <span className='dropdown-title'>AI</span>
            </Localized>
            <i className='fa fa-caret-down'></i>
          </button>
        </span>
      </Localized>
      {isDropdownOpen && (
        <ul className='dropdown-menu'>
          <Localized id='machinery-GoogleTranslation--option-rephrase'>
            <li
              data-characteristic='rephrased'
              onClick={handleOptionClick}
              title=''
            >
              REPHRASE
            </li>
          </Localized>
          <Localized id='machinery-GoogleTranslation--option-make-formal'>
            <li
              data-characteristic='formal'
              onClick={handleOptionClick}
              title=''
            >
              MAKE FORMAL
            </li>
          </Localized>
          <Localized id='machinery-GoogleTranslation--option-make-informal'>
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
              <Localized id='machinery-GoogleTranslation--option-show-original'>
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
  ) : (
    <li className='google-translation'>{title}</li>
  );
}

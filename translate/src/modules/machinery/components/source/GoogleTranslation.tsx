import React, { useState, useRef, useContext } from 'react';
import { Localized } from '@fluent/react';
import type { MachineryTranslation } from '~/api/machinery';
import { EntityView } from '~/context/EntityView';
import { Locale } from '~/context/Locale';
import { SearchData } from '~/context/SearchData';
import { logUXAction } from '~/api/uxaction';
import { useLLMTranslation } from '~/context/TranslationContext';
import { getEntityStringId } from '~/modules/machinery/getEntityStringId';
import { useAppSelector } from '~/hooks';
import { TERM } from '~/modules/terms';
import { TEAM_COMMENTS } from '~/modules/teamcomments/reducer';

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
  const { entity } = useContext(EntityView);
  const { query } = useContext(SearchData);

  const getLLMTranslationState = useLLMTranslation();
  const termState = useAppSelector((state) => state[TERM]);
  const teamCommentState = useAppSelector((state) => state[TEAM_COMMENTS]);

  let stringId: string | undefined;
  let stringComment: string | undefined;
  let groupComment: string | undefined;
  let resourceComment: string | undefined;
  let pinnedComments: string[] | undefined;
  if (!query) {
    stringId = getEntityStringId(entity);
    stringComment = entity.comment?.trim() || undefined;
    groupComment = entity.group_comment?.trim() || undefined;
    resourceComment = entity.resource_comment?.trim() || undefined;
    const pinned = teamCommentState.comments
      .filter((c) => c.pinned)
      .map((c) => {
        const doc = new DOMParser().parseFromString(c.content, 'text/html');
        return doc.body.textContent?.trim() ?? '';
      })
      .filter(Boolean);
    pinnedComments = pinned.length > 0 ? pinned : undefined;
  }

  const terms = termState.terms.length > 0 ? termState.terms : undefined;

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
      await transformLLMTranslation(
        translation,
        characteristic,
        locale.name,
        stringId,
        stringComment,
        groupComment,
        resourceComment,
        pinnedComments,
        terms,
      );
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
            <i className='fas fa-caret-down'></i>
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

import { Localized } from '@fluent/react';
import classNames from 'classnames';
import React, { useCallback, useContext, useEffect, useRef } from 'react';

import type { MachineryTranslation, SourceType } from '~/api/machinery';
import { logUXAction } from '~/api/uxaction';
import { EditorActions } from '~/context/Editor';
import { HelperSelection } from '~/context/HelperSelection';
import { Locale } from '~/context/Locale';
import { GenericTranslation } from '~/modules/translation';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

import { ConcordanceSearch } from './ConcordanceSearch';
import { MachineryTranslationSource } from './MachineryTranslationSource';
import { useLLMTranslation } from '~/context/TranslationContext';

import './ConcordanceSearch.css';
import './MachineryTranslation.css';

type Props = {
  sourceString: string;
  translation: MachineryTranslation;
  index: number;
};

/**
 * Render a Translation in the Machinery tab.
 *
 * Shows the original string and the translation, as well as a list of sources.
 * Similar translations (same original and translation) are shown only once
 * and their sources are merged.
 */
export function MachineryTranslationComponent({
  index,
  sourceString,
  translation,
}: Props): React.ReactElement<React.ElementType> {
  const { setEditorFromHelpers } = useContext(EditorActions);
  const { element, setElement } = useContext(HelperSelection);
  const isSelected = element === index;

  const getLLMTranslationState = useLLMTranslation();
  const { llmTranslation } = getLLMTranslationState(translation);

  const locale = useContext(Locale);

  const copyTranslationIntoEditor = useCallback(() => {
    if (window.getSelection()?.isCollapsed !== false) {
      setElement(index);
      const content = llmTranslation || translation.translation;
      const sources: SourceType[] = llmTranslation
        ? ['gpt-transform']
        : translation.sources;
      setEditorFromHelpers(content, sources, true);
      if (llmTranslation) {
        logUXAction('LLM Translation Copied', 'LLM Feature Adoption', {
          action: 'Copy LLM Translation',
          localeCode: locale.code,
        });
      }
    }
  }, [index, setEditorFromHelpers, translation, llmTranslation]);

  const className = classNames(
    'translation',
    useReadonlyEditor() && 'cannot-copy',
    isSelected && 'selected',
  );

  const translationRef = useRef<HTMLLIElement>(null);
  useEffect(() => {
    if (isSelected) {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      translationRef.current?.scrollIntoView({
        behavior: mediaQuery.matches ? 'auto' : 'smooth',
        block: 'nearest',
      });
    }
  }, [isSelected]);

  return (
    <Localized id='machinery-Translation--copy' attrs={{ title: true }}>
      <li
        className={className}
        title='Copy Into Translation (Ctrl + Shift + Down)'
        onClick={copyTranslationIntoEditor}
        ref={translationRef}
      >
        {translation.sources.includes('concordance-search') ? (
          <ConcordanceSearch
            sourceString={sourceString}
            translation={translation}
          />
        ) : (
          <MachineryTranslationSuggestion
            sourceString={sourceString}
            translation={translation}
          />
        )}
      </li>
    </Localized>
  );
}

function MachineryTranslationSuggestion({
  sourceString,
  translation,
}: {
  sourceString: string;
  translation: MachineryTranslation;
}) {
  const { code, direction, script } = useContext(Locale);

  const getLLMTranslationState = useLLMTranslation();
  const { llmTranslation, loading } = getLLMTranslationState(translation);

  return (
    <>
      <header>
        {translation.quality && (
          <span className='quality'>{translation.quality + '%'}</span>
        )}

        <MachineryTranslationSource translation={translation} />
      </header>
      <p className='original'>
        <GenericTranslation
          content={translation.original}
          diffTarget={
            // Caighdean takes `gd` translations as input, so we shouldn't
            // diff it against the `en-US` source string.
            translation.sources.includes('caighdean') ? undefined : sourceString
          }
        />
      </p>
      <p
        className='suggestion'
        dir={direction}
        data-script={script}
        lang={code}
      >
        {loading ? (
          <i className='fa fa-circle-notch fa-spin' />
        ) : (
          <GenericTranslation
            content={llmTranslation || translation.translation}
          />
        )}
      </p>
    </>
  );
}

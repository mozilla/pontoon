import { Localized } from '@fluent/react';
import classNames from 'classnames';
import React, { useCallback, useContext, useEffect, useRef } from 'react';

import { Locale } from '~/context/locale';
import type { MachineryTranslation } from '~/core/api';
import { NAME as EDITOR, useCopyMachineryTranslation } from '~/core/editor';
import { selectHelperElementIndex } from '~/core/editor/actions';
import { GenericTranslation } from '~/core/translation';
import { useAppDispatch, useAppSelector } from '~/hooks';

import { ConcordanceSearch } from './ConcordanceSearch';
import { TranslationSource } from './TranslationSource';

import './ConcordanceSearch.css';
import './Translation.css';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

type Props = {
  sourceString: string;
  translation: MachineryTranslation;
  index: number;
  entity: number | null;
};

/**
 * Render a Translation in the Machinery tab.
 *
 * Shows the original string and the translation, as well as a list of sources.
 * Similar translations (same original and translation) are shown only once
 * and their sources are merged.
 */
export function Translation({
  index,
  sourceString,
  translation,
  entity,
}: Props): React.ReactElement<React.ElementType> {
  const dispatch = useAppDispatch();

  const copyMachineryTranslation = useCopyMachineryTranslation(entity);
  const copyTranslationIntoEditor = useCallback(() => {
    dispatch(selectHelperElementIndex(index));
    copyMachineryTranslation(translation);
  }, [dispatch, index, translation, copyMachineryTranslation]);

  const selIdx = useAppSelector(
    (state) => state[EDITOR].selectedHelperElementIndex,
  );
  const changeSource = useAppSelector((state) => state[EDITOR].changeSource);
  const isSelected = changeSource === 'machinery' && selIdx === index;

  const className = classNames(
    'translation',
    useReadonlyEditor() && 'cannot-copy',
    isSelected && 'selected', // Highlight Machinery entries upon selection
  );

  const translationRef = useRef<HTMLLIElement>(null);
  useEffect(() => {
    if (selIdx === index) {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      translationRef.current?.scrollIntoView({
        behavior: mediaQuery.matches ? 'auto' : 'smooth',
        block: 'nearest',
      });
    }
  }, [selIdx, index]);

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
          <TranslationSuggestion
            sourceString={sourceString}
            translation={translation}
          />
        )}
      </li>
    </Localized>
  );
}

function TranslationSuggestion({
  sourceString,
  translation,
}: {
  sourceString: string;
  translation: MachineryTranslation;
}) {
  const { code, direction, script } = useContext(Locale);
  return (
    <>
      <header>
        {translation.quality && (
          <span className='quality'>{translation.quality + '%'}</span>
        )}
        <TranslationSource translation={translation} />
      </header>
      <p className='original'>
        <GenericTranslation
          content={translation.original}
          diffTarget={
            // Caighdean takes `gd` translations as input, so we shouldn't
            // diff it against the `en-US` source string.
            translation.sources.includes('caighdean') ? null : sourceString
          }
        />
      </p>
      <p
        className='suggestion'
        dir={direction}
        data-script={script}
        lang={code}
      >
        <GenericTranslation content={translation.translation} />
      </p>
    </>
  );
}

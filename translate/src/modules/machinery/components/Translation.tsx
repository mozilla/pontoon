import { Localized } from '@fluent/react';
import classNames from 'classnames';
import React, { useCallback, useContext, useEffect, useRef } from 'react';

import type { MachineryTranslation } from '~/api/machinery';
import { Locale } from '~/context/Locale';
import { EDITOR, useCopyMachineryTranslation } from '~/core/editor';
import { GenericTranslation } from '~/core/translation';
import { useAppDispatch, useAppSelector } from '~/hooks';

import { ConcordanceSearch } from './ConcordanceSearch';
import { TranslationSource } from './TranslationSource';

import './ConcordanceSearch.css';
import './Translation.css';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { HelperSelection } from '~/context/HelperSelection';

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
  const { element, setElement } = useContext(HelperSelection);
  const isSelected = element === index;

  const copyMachineryTranslation = useCopyMachineryTranslation(entity);
  const copyTranslationIntoEditor = useCallback(() => {
    setElement(index);
    copyMachineryTranslation(translation);
  }, [dispatch, index, translation, copyMachineryTranslation]);

  const changeSource = useAppSelector((state) => state[EDITOR].changeSource);

  const className = classNames(
    'translation',
    useReadonlyEditor() && 'cannot-copy',
    isSelected && changeSource === 'machinery' && 'selected',
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

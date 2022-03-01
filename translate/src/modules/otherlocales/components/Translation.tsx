import { Localized } from '@fluent/react';
import classNames from 'classnames';
import React, { useCallback, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';

import type { Entity, OtherLocaleTranslation } from '~/core/api';
import { NAME as EDITOR, useCopyOtherLocaleTranslation } from '~/core/editor';
import { selectHelperElementIndex } from '~/core/editor/actions';
import { isReadOnlyEditor } from '~/core/entities/selectors';
import type { NavigationParams } from '~/core/navigation';
import { TranslationProxy } from '~/core/translation';
import { useAppDispatch, useAppSelector } from '~/hooks';

import './Translation.css';

type Props = {
  entity: Entity;
  translation: OtherLocaleTranslation;
  parameters: NavigationParams;
  index: number;
};

/**
 * Render a Translation in the Locales tab.
 *
 * Show the translation of a given entity in a different locale, as well as the
 * locale and its code.
 */
export function Translation({
  entity,
  translation,
  parameters,
  index,
}: Props): React.ReactElement<React.ElementType> {
  const dispatch = useAppDispatch();
  const readonly = useAppSelector(isReadOnlyEditor);

  const selectedHelperElementIndex = useAppSelector(
    (state) => state[EDITOR].selectedHelperElementIndex,
  );
  const changeSource = useAppSelector((state) => state[EDITOR].changeSource);
  const isSelected =
    changeSource === 'otherlocales' && selectedHelperElementIndex === index;

  const className = classNames(
    'translation',
    readonly && 'cannot-copy',
    isSelected && 'selected',
  );

  const copyOtherLocaleTranslation = useCopyOtherLocaleTranslation();
  const copyTranslationIntoEditor = useCallback(() => {
    dispatch(selectHelperElementIndex(index));
    copyOtherLocaleTranslation(translation);
  }, [dispatch, index, translation, copyOtherLocaleTranslation]);

  const translationRef = useRef<HTMLLIElement>(null);
  useEffect(() => {
    if (selectedHelperElementIndex === index) {
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
      const behavior = mediaQuery.matches ? 'auto' : 'smooth';
      translationRef.current?.scrollIntoView?.({
        behavior: behavior,
        block: 'nearest',
      });
    }
  }, [selectedHelperElementIndex, index]);

  return (
    <Localized id='otherlocales-Translation--copy' attrs={{ title: true }}>
      <li
        className={className}
        title='Copy Into Translation (Ctrl + Shift + Down)'
        onClick={copyTranslationIntoEditor}
        ref={translationRef}
      >
        <header>
          {translation.locale.code === 'en-US' ? (
            <div>
              {translation.locale.name}
              <span>{translation.locale.code}</span>
            </div>
          ) : (
            <Localized
              id='otherlocales-Translation--header-link'
              attrs={{ title: true }}
              vars={{
                locale: translation.locale.name,
                code: translation.locale.code,
              }}
            >
              <Link
                to={`/${translation.locale.code}/${parameters.project}/${parameters.resource}/?string=${parameters.entity}`}
                target='_blank'
                rel='noopener noreferrer'
                title='Open string in { $locale } ({ $code })'
                onClick={(e: React.MouseEvent) => e.stopPropagation()}
              >
                {translation.locale.name}
                <span>{translation.locale.code}</span>
              </Link>
            </Localized>
          )}
        </header>
        <p
          lang={translation.locale.code}
          dir={translation.locale.direction}
          data-script={translation.locale.script}
        >
          <TranslationProxy
            content={translation.translation}
            format={entity.format}
          />
        </p>
      </li>
    </Localized>
  );
}

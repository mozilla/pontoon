import { Localized } from '@fluent/react';
import classNames from 'classnames';
import React, {
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from 'react';

import type { Entity } from '~/api/entity';
import type { OtherLocaleTranslation } from '~/api/other-locales';
import { EditorActions } from '~/context/Editor';
import { HelperSelection } from '~/context/HelperSelection';
import type { Location } from '~/context/Location';
import { TranslationProxy } from '~/core/translation';
import { getSimplePreview } from '~/core/utils/fluent';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

import './Translation.css';

type Props = {
  entity: Entity;
  translation: OtherLocaleTranslation;
  parameters: Location;
  index: number;
};

/**
 * Render a Translation in the Locales tab.
 *
 * Show the translation of a given entity in a different locale, as well as the
 * locale and its code.
 */
export function Translation({
  entity: { format },
  translation,
  parameters: { project, resource, entity },
  index,
}: Props): React.ReactElement<React.ElementType> {
  const { setEditorFromHelpers } = useContext(EditorActions);
  const { element, setElement } = useContext(HelperSelection);
  const [isCopied, setCopied] = useState(false);
  const isSelected = element === index;

  const copyTranslationIntoEditor = useCallback(() => {
    if (window.getSelection()?.isCollapsed !== false) {
      setElement(index);
      setCopied(true);
      const value =
        format === 'ftl'
          ? getSimplePreview(translation.translation)
          : translation.translation;
      setEditorFromHelpers(value, [], true);
    }
  }, [format, index, setEditorFromHelpers, translation]);

  const className = classNames(
    'translation',
    useReadonlyEditor() && 'cannot-copy',
    isSelected && isCopied && 'selected',
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
              <a
                href={`/${translation.locale.code}/${project}/${resource}/?string=${entity}`}
                target='_blank'
                rel='noopener noreferrer'
                title='Open string in { $locale } ({ $code })'
                onClick={(ev) => ev.stopPropagation()}
              >
                {translation.locale.name}
                <span>{translation.locale.code}</span>
              </a>
            </Localized>
          )}
        </header>
        <p
          lang={translation.locale.code}
          dir={translation.locale.direction}
          data-script={translation.locale.script}
        >
          <TranslationProxy content={translation.translation} format={format} />
        </p>
      </li>
    </Localized>
  );
}

import { Localized } from '@fluent/react';
import classNames from 'classnames';
import React, { useContext } from 'react';

import type { TermType } from '~/api/terminology';
import { EditorActions } from '~/context/Editor';
import { Locale } from '~/context/Locale';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

import './Term.css';

type Props = {
  navigateToPath: (arg0: string) => void;
  term: TermType;
};

/**
 * Shows term entry with its metadata.
 */
export function Term({ navigateToPath, term }: Props): React.ReactElement {
  const { code } = useContext(Locale);
  const isReadOnlyEditor = useReadonlyEditor();
  const { setEditorSelection } = useContext(EditorActions);

  const copyTermIntoEditor = () => {
    if (
      !isReadOnlyEditor &&
      term.translation &&
      window.getSelection()?.isCollapsed !== false
    ) {
      setEditorSelection(term.translation);
    }
  };

  const handleLinkClick = (ev: React.MouseEvent<HTMLAnchorElement>) => {
    ev.preventDefault();
    ev.stopPropagation();
    navigateToPath(ev.currentTarget.pathname);
  };

  const cn = classNames(
    'term',
    isReadOnlyEditor || !term.translation ? 'cannot-copy' : null,
  );

  return (
    <Localized id='term-Term--copy' attrs={{ title: true }}>
      <li
        className={cn}
        title='Copy Into Translation'
        onClick={copyTermIntoEditor}
      >
        <header>
          <span className='text'>{term.text}</span>
          <span className='part-of-speech'>{term.partOfSpeech}</span>
          <a
            href={`/${code}/terminology/common/?string=${term.entityId}`}
            onClick={handleLinkClick}
            className='translate'
          >
            Translate
          </a>
        </header>
        <p className='translation'>{term.translation}</p>
        <div className='details'>
          <p className='definition'>{term.definition}</p>
          {!term.usage ? null : (
            <p className='usage'>
              <Localized id='term-Term--for-example'>
                <span className='title'>E.G.</span>
              </Localized>
              <span className='content'>{term.usage}</span>
            </p>
          )}
        </div>
      </li>
    </Localized>
  );
}

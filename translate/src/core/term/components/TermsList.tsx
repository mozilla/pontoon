import React from 'react';

import type { TermType } from '~/api/terminology';
import { Locale } from '~/context/locale';

import { Term } from './Term';
import './TermsList.css';

type Props = {
  isReadOnlyEditor: boolean;
  terms: Array<TermType>;
  addTextToEditorTranslation: (arg0: string) => void;
  navigateToPath: (arg0: string) => void;
};

/**
 * Shows a list of terms.
 */
export function TermsList(props: Props): React.ReactElement<'ul'> {
  const { code } = React.useContext(Locale);
  return (
    <ul className='terms-list'>
      {props.terms.map((term, i) => {
        return (
          <Term
            key={i}
            isReadOnlyEditor={props.isReadOnlyEditor}
            locale={code}
            term={term}
            addTextToEditorTranslation={props.addTextToEditorTranslation}
            navigateToPath={props.navigateToPath}
          />
        );
      })}
    </ul>
  );
}

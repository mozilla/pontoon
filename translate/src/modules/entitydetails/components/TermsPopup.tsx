import React, { useRef } from 'react';

import type { TermType } from '~/core/api';
import { TermsList } from '~/core/term';
import { useOnDiscard } from '~/core/utils';

import './TermsPopup.css';

type Props = {
  readonly isReadOnlyEditor: boolean;
  readonly terms: Array<TermType>;
  readonly addTextToEditorTranslation: (text: string) => void;
  readonly hide: () => void;
  readonly navigateToPath: (path: string) => void;
};

/**
 * Shows a popup with a list of all terms belonging to the highlighted one.
 */
export default function TermsPopup(props: Props): React.ReactElement<'div'> {
  const ref = useRef(null);
  useOnDiscard(ref, props.hide);

  return (
    <div ref={ref} className='terms-popup' onClick={props.hide}>
      <TermsList
        isReadOnlyEditor={props.isReadOnlyEditor}
        terms={props.terms}
        addTextToEditorTranslation={props.addTextToEditorTranslation}
        navigateToPath={props.navigateToPath}
      />
    </div>
  );
}

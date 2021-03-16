/* @flow */

import * as React from 'react';

import './TermsPopup.css';

import { TermsList } from 'core/term';
import { useOnDiscard } from 'core/utils';

import type { TermType } from 'core/api';

type Props = {|
    +isReadOnlyEditor: boolean,
    +locale: string,
    +terms: Array<TermType>,
    +addTextToEditorTranslation: (string) => void,
    +hide: () => void,
    +navigateToPath: (string) => void,
|};

/**
 * Shows a popup with a list of all terms belonging to the highlighted one.
 */
export default function TermsPopup(props: Props): React.Element<'div'> {
    const ref = React.useRef(null);
    useOnDiscard(ref, props.hide);

    return (
        <div ref={ref} className='terms-popup' onClick={props.hide}>
            <TermsList
                isReadOnlyEditor={props.isReadOnlyEditor}
                locale={props.locale}
                terms={props.terms}
                addTextToEditorTranslation={props.addTextToEditorTranslation}
                navigateToPath={props.navigateToPath}
            />
        </div>
    );
}

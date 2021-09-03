import * as React from 'react';

import './TermsPopup.css';

import { TermsList } from 'core/term';
import { useOnDiscard } from 'core/utils';

import type { TermType } from 'core/api';

type Props = {
    readonly isReadOnlyEditor: boolean;
    readonly locale: string;
    readonly terms: Array<TermType>;
    readonly addTextToEditorTranslation: (text: string) => void;
    readonly hide: () => void;
    readonly navigateToPath: (path: string) => void;
};

/**
 * Shows a popup with a list of all terms belonging to the highlighted one.
 */
export default function TermsPopup(props: Props): React.ReactElement<'div'> {
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

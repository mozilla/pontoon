import * as React from 'react';

import './TermsList.css';

import Term from './Term';

import type { TermType } from 'core/api';

type Props = {
    isReadOnlyEditor: boolean;
    locale: string;
    terms: Array<TermType>;
    addTextToEditorTranslation: (arg0: string) => void;
    navigateToPath: (arg0: string) => void;
};

/**
 * Shows a list of terms.
 */
export default function TermsList(props: Props): React.ReactElement<'ul'> {
    return (
        <ul className='terms-list'>
            {props.terms.map((term, i) => {
                return (
                    <Term
                        key={i}
                        isReadOnlyEditor={props.isReadOnlyEditor}
                        locale={props.locale}
                        term={term}
                        addTextToEditorTranslation={
                            props.addTextToEditorTranslation
                        }
                        navigateToPath={props.navigateToPath}
                    />
                );
            })}
        </ul>
    );
}

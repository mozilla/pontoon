import * as React from 'react';
import { Localized } from '@fluent/react';

import './Terms.css';

import { TermsList } from 'core/term';

import { TermState } from 'core/term';

type Props = {
    isReadOnlyEditor: boolean;
    locale: string;
    terms: TermState;
    addTextToEditorTranslation: (arg0: string) => void;
    navigateToPath: (arg0: string) => void;
};

/**
 * Shows all terms found in the source string.
 */
export default function Terms(props: Props) {
    let { terms } = props;

    if (terms.fetching || !terms.terms) {
        return null;
    }

    terms = terms.terms;

    return (
        <section className='terms'>
            {!terms.length ? (
                <Localized id='entitydetails-Helpers--no-terms'>
                    <p className='no-terms'>No terms available.</p>
                </Localized>
            ) : (
                <TermsList
                    isReadOnlyEditor={props.isReadOnlyEditor}
                    locale={props.locale}
                    terms={terms}
                    addTextToEditorTranslation={
                        props.addTextToEditorTranslation
                    }
                    navigateToPath={props.navigateToPath}
                />
            )}
        </section>
    );
}

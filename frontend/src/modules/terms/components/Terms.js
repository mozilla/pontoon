/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './Terms.css';

import { TermsList } from 'core/term';

import type { TermState } from 'core/term';

type Props = {|
    isReadOnlyEditor: boolean,
    locale: string,
    terms: TermState,
    addTextToEditorTranslation: (string) => void,
    navigateToPath: (string) => void,
|};

/**
 * Shows all terms found in the source string.
 */
export default function Terms(props: Props): null | React.Element<'section'> {
    const { terms } = props;

    if (terms.fetching || !terms.terms) {
        return null;
    }

    const termlist = terms.terms;

    return (
        <section className='terms'>
            {!termlist.length ? (
                <Localized id='entitydetails-Helpers--no-terms'>
                    <p className='no-terms'>No terms available.</p>
                </Localized>
            ) : (
                <TermsList
                    isReadOnlyEditor={props.isReadOnlyEditor}
                    locale={props.locale}
                    terms={termlist}
                    addTextToEditorTranslation={
                        props.addTextToEditorTranslation
                    }
                    navigateToPath={props.navigateToPath}
                />
            )}
        </section>
    );
}

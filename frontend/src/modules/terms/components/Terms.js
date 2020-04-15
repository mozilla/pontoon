/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './Terms.css';

import { TermsList } from 'core/term';

import type { TermState } from 'core/term';

type Props = {|
    isReadOnlyEditor: boolean,
    terms: TermState,
    addTextToEditorTranslation: (string) => void,
|};


/**
 * Shows all terms found in the source string.
 */
export default function Terms(props: Props) {
    let { isReadOnlyEditor, terms, addTextToEditorTranslation } = props;

    if (terms.fetching || !terms.terms) {
        return null;
    }

    terms = terms.terms;

    return <section className="terms">
        { !terms.length ?
            <Localized id="entitydetails-Helpers--no-terms">
                <p className="no-terms">No terms available.</p>
            </Localized>
            :
            <TermsList
                terms={ terms }
                isReadOnlyEditor={ isReadOnlyEditor }
                addTextToEditorTranslation={ addTextToEditorTranslation }            
            />
        }
    </section>;
}

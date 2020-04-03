/* @flow */

import * as React from 'react';

import './TermsList.css';

import Term from './Term';

import type { TermType } from 'core/api';

type Props = {|
    terms: Array<TermType>,
    isReadOnlyEditor: boolean,
    addTextToEditorTranslation: (string) => void,
|};


/**
 * Shows a list of terms.
 */
export default function TermsList(props: Props) {
    return <ul className="terms-list">
        { props.terms.map((term, i) => {
            return <Term
                key={ i }
                term={ term }
                isReadOnlyEditor={ props.isReadOnlyEditor }
                addTextToEditorTranslation={ props.addTextToEditorTranslation }
            />;
        }) }
    </ul>;
}

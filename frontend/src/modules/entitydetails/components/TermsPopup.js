/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';

import './TermsPopup.css';

import { TermsList } from 'core/term';

import type { TermType } from 'core/api';


type Props = {|
    +isReadOnlyEditor: boolean,
    +terms: Array<TermType>,
    +addTextToEditorTranslation: (string) => void,
    +hide: () => void,
|};


/**
 * Shows a popup with a list of all terms belonging to the highlighted one.
 */
export function TermsPopup(props: Props) {
    const { terms } = props;

    // This method is called by the Higher-Order Component `onClickOutside`
    // when a user clicks outside this component.
    TermsPopup.handleClickOutside = () => props.hide();

    if (!terms.length) {
        return null;
    }

    return <div className="terms-popup" onClick={ props.hide }>
        <TermsList
            terms={ terms }
            isReadOnlyEditor={ props.isReadOnlyEditor }
            addTextToEditorTranslation={ props.addTextToEditorTranslation }
        />
    </div>;
}


const clickOutsideConfig = {
    handleClickOutside: () => TermsPopup.handleClickOutside
};

export default onClickOutside(TermsPopup, clickOutsideConfig);

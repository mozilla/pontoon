/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import type { EntityTranslation } from 'core/api';
import type { ChangeOperation } from 'modules/history';


type Props = {
    isTranslator: boolean,
    forceSuggestions: boolean,
    sameExistingTranslation: ?EntityTranslation,
    sendTranslation: () => void,
    updateTranslationStatus: (number, ChangeOperation, ?boolean) => void,
};


/**
 * Render the main action button of the Editor.
 *
 * This component renders a button to "Save", "Suggest" or "Approve" a translation.
 *
 * It renders "Approve" if the translation in the Editor is the same as an
 * already existing translation for that same entity and locale, and the user
 * has permission to approve.
 * Otherwise, if the "force suggestion" user setting is on, it renders "Suggest".
 * Otherwise, it renders "Save".
 */
export default function EditorMainAction(props: Props) {
    const {
        isTranslator,
        forceSuggestions,
        sameExistingTranslation,
        sendTranslation,
        updateTranslationStatus,
    } = props;

    function approveTranslation() {
        if (sameExistingTranslation) {
            updateTranslationStatus(sameExistingTranslation.pk, 'approve');
        }
    }

    if (isTranslator && sameExistingTranslation && !sameExistingTranslation.approved) {
        // Approve button, will approve the translation.
        return <Localized
            id="editor-EditorMenu--button-approve"
            attrs={{ title: true }}
        >
            <button
                className="action-approve"
                onClick={ approveTranslation }
                title="Approve Translation (Enter)"
            >
                Approve
            </button>
        </Localized>;
    }

    if (forceSuggestions || !isTranslator) {
        // Suggest button, will send an unreviewed translation.
        return <Localized
            id="editor-EditorMenu--button-suggest"
            attrs={{ title: true }}
        >
            <button
                className="action-suggest"
                onClick={ sendTranslation }
                title="Suggest Translation (Enter)"
            >
                Suggest
            </button>
        </Localized>;
    }

    // Save button, will send an approved translation.
    return <Localized
        id="editor-EditorMenu--button-save"
        attrs={{ title: true }}
    >
        <button
            className="action-save"
            onClick={ sendTranslation }
            title="Save Translation (Enter)"
        >
            Save
        </button>
    </Localized>;
}

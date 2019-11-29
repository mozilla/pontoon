/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import type { EntityTranslation } from 'core/api';
import type { ChangeOperation, HistoryState } from 'modules/history';
import type { Translation } from '..';


type Props = {
    activeTranslation: EntityTranslation,
    initialTranslation: Translation,
    isTranslator: boolean,
    forceSuggestions: boolean,
    history: HistoryState,
    translation: Translation,
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
        activeTranslation,
        initialTranslation,
        isTranslator,
        forceSuggestions,
        history,
        translation,
        sendTranslation,
        updateTranslationStatus,
    } = props;

    let sameTranslationAs = null;
    if (translation) {
        if (translation === initialTranslation) {
            sameTranslationAs = activeTranslation;
        }
        else if (history.translations.length) {
            sameTranslationAs = history.translations.find(t => t.string === translation)
        }
    }

    function approveTranslation() {
        if (sameTranslationAs) {
            updateTranslationStatus(sameTranslationAs.pk, 'approve');
        }
    }

    if (isTranslator && sameTranslationAs && !sameTranslationAs.approved) {
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

    if (forceSuggestions) {
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

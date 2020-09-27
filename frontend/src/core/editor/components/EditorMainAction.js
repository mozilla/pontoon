/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import type { EntityTranslation } from 'core/api';
import type { ChangeOperation } from 'modules/history';

type Props = {
    isRunningRequest: boolean,
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
        isRunningRequest,
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

    let btn: {
        id: string,
        className: string,
        action: Function,
        title: string,
        label: string,
        glyph: ?React.Node,
    };

    if (
        isTranslator &&
        sameExistingTranslation &&
        !sameExistingTranslation.approved
    ) {
        // Approve button, will approve the translation.
        btn = {
            id: 'editor-EditorMenu--button-approve',
            className: 'action-approve',
            action: approveTranslation,
            title: 'Approve Translation (Enter)',
            label: 'Approve',
            glyph: null,
        };

        if (isRunningRequest) {
            btn.id = 'editor-EditorMenu--button-approving';
            btn.label = 'Approving';
            btn.glyph = <i className='fa fa-circle-notch fa-spin' />;
        }
    } else if (forceSuggestions || !isTranslator) {
        // Suggest button, will send an unreviewed translation.
        btn = {
            id: 'editor-EditorMenu--button-suggest',
            className: 'action-suggest',
            action: sendTranslation,
            title: 'Suggest Translation (Enter)',
            label: 'Suggest',
            glyph: null,
        };

        if (isRunningRequest) {
            btn.id = 'editor-EditorMenu--button-suggesting';
            btn.label = 'Suggesting';
            btn.glyph = <i className='fa fa-circle-notch fa-spin' />;
        }
    } else {
        // Save button, will send an approved translation.
        btn = {
            id: 'editor-EditorMenu--button-save',
            className: 'action-save',
            action: sendTranslation,
            title: 'Save Translation (Enter)',
            label: 'Save',
            glyph: null,
        };

        if (isRunningRequest) {
            btn.id = 'editor-EditorMenu--button-saving';
            btn.label = 'Saving';
            btn.glyph = <i className='fa fa-circle-notch fa-spin' />;
        }
    }

    return (
        <Localized id={btn.id} attrs={{ title: true }} glyph={btn.glyph}>
            <button
                className={btn.className}
                onClick={btn.action}
                title={btn.title}
                disabled={isRunningRequest}
            >
                {btn.glyph}
                {btn.label}
            </button>
        </Localized>
    );
}

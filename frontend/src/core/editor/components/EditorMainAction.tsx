import * as React from 'react';
import { Localized } from '@fluent/react';

import { useAppSelector } from 'hooks';
import * as user from 'core/user';

import * as editor from '..';

type Props = {
    sendTranslation: (ignoreWarnings?: boolean) => void;
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
export default function EditorMainAction(
    props: Props,
): React.ReactElement<React.ElementType> {
    const isRunningRequest = useAppSelector(
        (state) => state.editor.isRunningRequest,
    );
    const forceSuggestions = useAppSelector(
        (state) => state.user.settings.forceSuggestions,
    );
    const isTranslator = useAppSelector((state) =>
        user.selectors.isTranslator(state),
    );
    const sameExistingTranslation = useAppSelector((state) =>
        editor.selectors.sameExistingTranslation(state),
    );

    const updateTranslationStatus = editor.useUpdateTranslationStatus();

    function approveTranslation() {
        if (sameExistingTranslation) {
            updateTranslationStatus(sameExistingTranslation.pk, 'approve');
        }
    }

    let btn: {
        id: string;
        className: string;
        action: (...args: Array<any>) => any;
        title: string;
        label: string;
        glyph: React.ReactElement<'i'> | null | undefined;
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
            label: 'APPROVE',
            glyph: null,
        };

        if (isRunningRequest) {
            btn.id = 'editor-EditorMenu--button-approving';
            btn.label = 'APPROVING';
            btn.glyph = <i className='fa fa-circle-notch fa-spin' />;
        }
    } else if (forceSuggestions || !isTranslator) {
        // Suggest button, will send an unreviewed translation.
        btn = {
            id: 'editor-EditorMenu--button-suggest',
            className: 'action-suggest',
            action: props.sendTranslation,
            title: 'Suggest Translation (Enter)',
            label: 'SUGGEST',
            glyph: null,
        };

        if (isRunningRequest) {
            btn.id = 'editor-EditorMenu--button-suggesting';
            btn.label = 'SUGGESTING';
            btn.glyph = <i className='fa fa-circle-notch fa-spin' />;
        }
    } else {
        // Save button, will send an approved translation.
        btn = {
            id: 'editor-EditorMenu--button-save',
            className: 'action-save',
            action: props.sendTranslation,
            title: 'Save Translation (Enter)',
            label: 'SAVE',
            glyph: null,
        };

        if (isRunningRequest) {
            btn.id = 'editor-EditorMenu--button-saving';
            btn.label = 'SAVING';
            btn.glyph = <i className='fa fa-circle-notch fa-spin' />;
        }
    }

    return (
        <Localized
            id={btn.id}
            attrs={{ title: true }}
            elems={{ glyph: btn.glyph }}
        >
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

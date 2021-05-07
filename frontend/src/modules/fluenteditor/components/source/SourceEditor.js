/* @flow */

import * as React from 'react';

import * as editor from 'core/editor';

import { GenericTranslationForm } from 'modules/genericeditor';

type Props = {
    ftlSwitch: React.Node,
};

/**
 * Editor for complex Fluent strings.
 *
 * Displayed when the Rich Editor cannot handle the translation, or if a user
 * forces showing the Fluent source.
 */
export default function SourceEditor(props: Props): React.Element<any> {
    const clearEditor = editor.useClearEditor();
    const copyOriginalIntoEditor = editor.useCopyOriginalIntoEditor();
    const sendTranslation = editor.useSendTranslation();
    const updateTranslation = editor.useUpdateTranslation();

    return (
        <>
            <GenericTranslationForm
                sendTranslation={sendTranslation}
                updateTranslation={updateTranslation}
            />
            <editor.EditorMenu
                firstItemHook={props.ftlSwitch}
                clearEditor={clearEditor}
                copyOriginalIntoEditor={copyOriginalIntoEditor}
                sendTranslation={sendTranslation}
            />
        </>
    );
}

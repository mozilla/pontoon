/* @flow */

import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';

import * as editor from 'core/editor';
import * as entities from 'core/entities';
import { fluent } from 'core/utils';

import RichTranslationForm from './RichTranslationForm';


type Props = {
    ftlSwitch: React.Node,
};


/**
 * Rich Editor for supported Fluent strings.
 *
 * This shows the Fluent translation based on its AST, presenting a nicer
 * interface to the user. The translation is stored as an AST, and changes
 * are made directly to that AST. That is why lots of Editor methods are
 * overwritten, to handle the convertion from AST to string and back.
 */
export default function RichEditor(props: Props) {
    const dispatch = useDispatch();

    const sendTranslation = editor.useSendTranslation();
    const updateTranslation = editor.useUpdateTranslation();

    const translation = useSelector(state => state.editor.translation);
    const entity = useSelector(state => entities.selectors.getSelectedEntity(state));
    const locale = useSelector(state => state.locale);

    React.useEffect(() => {
        if (typeof(translation) === 'string') {
            const message = fluent.parser.parseEntry(translation);
            updateTranslation(message);
        }
    }, [translation, updateTranslation, dispatch]);

    function clearEditor() {
        if (entity) {
            updateTranslation(
                fluent.getEmptyMessage(
                    fluent.parser.parseEntry(entity.original),
                    locale,
                )
            );
        }
    }

    function copyOriginalIntoEditor() {
        if (entity) {
            updateTranslation(fluent.parser.parseEntry(entity.original));
        }
    }

    function sendFluentTranslation(ignoreWarnings?: boolean) {
        const fluentString = fluent.serializer.serializeEntry(translation);
        sendTranslation(ignoreWarnings, fluentString);
    }

    return (
        <>
            <RichTranslationForm
                clearEditor={ clearEditor }
                copyOriginalIntoEditor={ copyOriginalIntoEditor }
                sendTranslation={ sendFluentTranslation }
                updateTranslation={ updateTranslation }
            />
            <editor.EditorMenu
                firstItemHook={ props.ftlSwitch }
                clearEditor={ clearEditor }
                copyOriginalIntoEditor={ copyOriginalIntoEditor }
                sendTranslation={ sendFluentTranslation }
            />
        </>
    );
}

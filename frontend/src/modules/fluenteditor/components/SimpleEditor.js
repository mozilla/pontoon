/* @flow */

import * as React from 'react';

import * as editor from 'core/editor';
import { fluent } from 'core/utils';
import { GenericTranslationForm } from 'modules/genericeditor';

import type { EditorProps } from 'core/editor';


type Props = {
    ...EditorProps,
    ftlSwitch: React.Node,
};


/**
 * Editor for simple Fluent strings.
 */
export default class SimpleEditor extends React.Component<Props> {
    componentDidUpdate(prevProps: Props) {
        const props = this.props;
        if (
            props.entity &&
            props.editor.translation !== prevProps.editor.translation &&
            props.editor.changeSource === 'external' &&
            typeof(props.editor.translation) === 'string'
        ) {
            this.updateFluentTranslation(props.editor.translation);
        }
    }

    updateFluentTranslation(translation: string) {
        const message = fluent.parser.parseEntry(translation);
        if (
            fluent.isSimpleMessage(message) ||
            fluent.isSimpleSingleAttributeMessage(message)
        ) {
            this.props.updateTranslation(
                fluent.getSimplePreview(translation),
                true,
            );
        }
    }

    sendTranslation = (ignoreWarnings?: boolean, translation?: string) => {
        const entity = this.props.entity;
        if (!entity) {
            return;
        }

        const currentTranslation = translation || this.props.editor.translation;

        if (typeof(currentTranslation) !== 'string') {
            // This should never happen. If it does, the developers have made a
            // mistake in the code. We need this check for Flow's sake though.
            throw new Error('Unexpected data type for translation: ' + typeof(translation));
        }

        const content = fluent.serializer.serializeEntry(
            fluent.getReconstructedMessage(entity.original, currentTranslation)
        );
        this.props.sendTranslation(ignoreWarnings, content);
    }

    render() {
        const { ftlSwitch, ...props } = this.props;

        return <>
            <GenericTranslationForm
                { ...props }
                sendTranslation={ this.sendTranslation }
            />
            <editor.EditorMenu
                { ...props }
                firstItemHook={ ftlSwitch }
                sendTranslation={ this.sendTranslation }
            />
        </>;
    }
}

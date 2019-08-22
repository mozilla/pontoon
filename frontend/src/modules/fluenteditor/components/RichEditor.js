/* @flow */

import * as React from 'react';

import * as editor from 'core/editor';
import { fluent } from 'core/utils';

import RichTranslationForm from './RichTranslationForm';

import type { EditorProps, Translation } from 'core/editor';


type Props = {
    ...EditorProps,
    ftlSwitch: React.Node,
};


/**
 * Editor for simple Fluent strings.
 */
export default class RichEditor extends React.Component<Props> {
    componentDidUpdate(prevProps: Props) {
        const props = this.props;
        const translation = props.editor.translation;

        if (
            props.entity &&
            translation !== prevProps.editor.translation &&
            props.editor.changeSource === 'external' &&
            typeof(translation) === 'string'
        ) {
            let message = fluent.parser.parseEntry(translation);

            if (message.type === 'Junk') {
                message = fluent.getReconstructedMessage(
                    props.entity.original,
                    translation,
                );
            }

            props.updateTranslation(message);
        }
    }

    clearEditor = () => {
        const { entity } = this.props;
        if (entity) {
            this.props.updateTranslation(
                fluent.getEmptyMessage(
                    fluent.parser.parseEntry(entity.original)
                )
            );
        }
    }

    copyOriginalIntoEditor = () => {
        const { entity } = this.props;
        if (entity) {
            this.props.updateTranslation(fluent.parser.parseEntry(entity.original), true);
        }
    }

    sendTranslation = (ignoreWarnings?: boolean, translation?: Translation) => {
        const message = translation || this.props.editor.translation;
        const fluentString = fluent.serializer.serializeEntry(message);

        this.props.sendTranslation(ignoreWarnings, fluentString);
    }

    updateUnsavedChanges = (translation?: Translation, initial?: Translation) => {
        const props = this.props;

        if (!translation) {
            translation = props.editor.translation;
        }

        if (!initial) {
            initial = props.editor.initialTranslation;
        }

        this.props.updateUnsavedChanges(
            fluent.serializer.serializeEntry(translation),
            fluent.serializer.serializeEntry(initial),
        );
    }

    render() {
        const { ftlSwitch, ...props } = this.props;

        return <>
            <RichTranslationForm
                { ...props }
                clearEditor={ this.clearEditor }
                copyOriginalIntoEditor={ this.copyOriginalIntoEditor }
                sendTranslation={ this.sendTranslation }
                updateUnsavedChanges={ this.updateUnsavedChanges }
            />
            <editor.EditorMenu
                { ...props }
                firstItemHook={ ftlSwitch }
                clearEditor={ this.clearEditor }
                copyOriginalIntoEditor={ this.copyOriginalIntoEditor }
                sendTranslation={ this.sendTranslation }
            />
        </>;
    }
}

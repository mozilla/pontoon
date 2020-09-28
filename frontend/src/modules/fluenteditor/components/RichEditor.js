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
 * Rich Editor for supported Fluent strings.
 *
 * This shows the Fluent translation based on its AST, presenting a nicer
 * interface to the user. The translation is stored as an AST, and changes
 * are made directly to that AST. That is why lots of Editor methods are
 * overwritten, to handle the convertion from AST to string and back.
 */
export default class RichEditor extends React.Component<Props> {
    componentDidUpdate(prevProps: Props) {
        const props = this.props;
        const translation = props.editor.translation;

        if (
            props.entity &&
            translation !== prevProps.editor.translation &&
            props.editor.changeSource !== 'internal' &&
            this.props.editor.changeSource !== 'machinery' &&
            typeof translation === 'string'
        ) {
            let message = fluent.parser.parseEntry(translation);

            if (message.type === 'Junk') {
                message = fluent.getReconstructedMessage(
                    props.entity.original,
                    translation,
                );
            }

            props.updateTranslation(message, true);
        }
    }

    clearEditor = () => {
        const { entity, locale } = this.props;
        if (entity) {
            this.props.updateTranslation(
                fluent.getEmptyMessage(
                    fluent.parser.parseEntry(entity.original),
                    locale,
                ),
                true,
            );
        }
    };

    copyOriginalIntoEditor = () => {
        const { entity } = this.props;
        if (entity) {
            this.props.updateTranslation(
                fluent.parser.parseEntry(entity.original),
                true,
            );
        }
    };

    sendTranslation = (ignoreWarnings?: boolean, translation?: Translation) => {
        const message = translation || this.props.editor.translation;
        const fluentString = fluent.serializer.serializeEntry(message);
        this.props.sendTranslation(ignoreWarnings, fluentString, message);
    };

    updateUnsavedChanges = (
        translation?: Translation,
        initial?: Translation,
    ) => {
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
    };

    render() {
        const { ftlSwitch, ...props } = this.props;

        return (
            <>
                <RichTranslationForm
                    {...props}
                    clearEditor={this.clearEditor}
                    copyOriginalIntoEditor={this.copyOriginalIntoEditor}
                    sendTranslation={this.sendTranslation}
                    updateUnsavedChanges={this.updateUnsavedChanges}
                />
                <editor.EditorMenu
                    {...props}
                    firstItemHook={ftlSwitch}
                    clearEditor={this.clearEditor}
                    copyOriginalIntoEditor={this.copyOriginalIntoEditor}
                    sendTranslation={this.sendTranslation}
                />
            </>
        );
    }
}

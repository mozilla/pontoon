/* @flow */

import * as React from 'react';

import * as editor from 'core/editor';
import * as plural from 'core/plural';

import GenericTranslationForm from './GenericTranslationForm';

import type { EditorProps } from 'core/editor';

export class EditorBase extends React.Component<EditorProps> {
    componentDidMount() {
        this.props.setInitialTranslation(this.props.activeTranslationString);
        this.props.updateTranslation(this.props.activeTranslationString, true);
    }

    componentDidUpdate(prevProps: EditorProps) {
        const { pluralForm, entity, activeTranslationString } = this.props;

        if (
            pluralForm !== prevProps.pluralForm ||
            entity !== prevProps.entity
        ) {
            this.props.setInitialTranslation(activeTranslationString);
            this.props.updateTranslation(activeTranslationString, true);
        }
    }

    render() {
        const props = this.props;

        // Because Flow.
        if (typeof props.editor.translation !== 'string') {
            return null;
        }

        // Transitional state when switching view despite unsaved changes.
        if (!props.entity) {
            return null;
        }

        const original =
            props.pluralForm <= 0
                ? props.entity.original
                : props.entity.original_plural;

        return (
            <>
                <plural.PluralSelector />
                <GenericTranslationForm {...props} />
                <editor.EditorMenu
                    {...props}
                    translationLengthHook={
                        <editor.TranslationLength
                            comment={props.entity.comment}
                            format={props.entity.format}
                            original={original}
                            translation={props.editor.translation}
                        />
                    }
                />
            </>
        );
    }
}

export default editor.connectedEditor(EditorBase);

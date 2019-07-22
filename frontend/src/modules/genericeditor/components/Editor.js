/* @flow */

import * as React from 'react';

import * as editor from 'core/editor';
import * as plural from 'core/plural';

import GenericTranslationForm from './GenericTranslationForm';

import type { EditorProps } from 'core/editor';


export class EditorBase extends React.Component<EditorProps> {
    componentDidMount() {
        this.props.updateTranslation(this.props.activeTranslation);
    }

    componentDidUpdate(prevProps: EditorProps) {
        const { pluralForm, entity, activeTranslation } = this.props;

        if (
            pluralForm !== prevProps.pluralForm ||
            entity !== prevProps.entity
        ) {
            this.props.updateTranslation(activeTranslation);
        }
    }

    render() {
        const props = this.props;

        return <>
            <plural.PluralSelector />
            <GenericTranslationForm { ...props } />
            <editor.EditorMenu { ...props } />
        </>;
    }
}


export default editor.connectedEditor(EditorBase);

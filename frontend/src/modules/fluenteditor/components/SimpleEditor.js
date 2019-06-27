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
            props.editor.changeSource === 'external'
        ) {
            const message = fluent.parser.parseEntry(props.editor.translation);
            if (fluent.isSimpleMessage(message)) {
                props.updateTranslation(
                    fluent.getSimplePreview(props.editor.translation),
                    true,
                );
            }
        }
    }

    sendTranslation = (ignoreWarnings?: boolean, translation?: string) => {
        const entity = this.props.entity;
        if (!entity) {
            return;
        }

        if (!translation) {
            translation = this.props.editor.translation;
        }

        const content = fluent.getReconstructedSimpleMessage(entity.original, translation);
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

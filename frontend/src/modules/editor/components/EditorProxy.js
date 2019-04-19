/* @flow */

import * as React from 'react';

import FluentEditor from './FluentEditor';
import GenericEditor from './GenericEditor';

import type { DbEntity } from 'modules/entitieslist';
import type { EditorProps } from './GenericEditor';


type EditorProxyProps = {|
    ...EditorProps,
    entity: ?DbEntity,
|};


/*
 * Renders an appropriate Editor for an entity, based on its file format.
 *
 * Currently:
 *   - fluent (ftl) -> FluentEditor
 *   - default -> GenericEditor
 */
export default class EditorProxy extends React.Component<EditorProxyProps> {
    componentDidUpdate(prevProps: EditorProxyProps) {
        // Close failed checks popup when content of the editor changes,
        // but only if the errors and warnings did not change
        // meaning they were already shown in the previous render
        const prevEditor = prevProps.editor;
        const editor = this.props.editor;
        if (
            prevEditor.translation !== editor.translation &&
            prevEditor.errors === editor.errors &&
            prevEditor.warnings === editor.warnings &&
            (editor.errors.length || editor.warnings.length)
        ) {
            this.props.resetFailedChecks();
        }
    }

    render() {
        const { entity } = this.props;

        if (!entity) {
            return null;
        }

        if (entity.format === 'ftl') {
            return <FluentEditor
                key={ entity.pk }
                isReadOnlyEditor={ this.props.isReadOnlyEditor }
                editor={ this.props.editor }
                locale={ this.props.locale }
                copyOriginalIntoEditor={ this.props.copyOriginalIntoEditor }
                resetFailedChecks={ this.props.resetFailedChecks }
                resetSelectionContent={ this.props.resetSelectionContent }
                sendTranslation={ this.props.sendTranslation }
                updateTranslation={ this.props.updateTranslation }
                updateTranslationStatus={ this.props.updateTranslationStatus }
            />;
        }

        return <GenericEditor
            key={ entity.pk }
            isReadOnlyEditor={ this.props.isReadOnlyEditor }
            editor={ this.props.editor }
            locale={ this.props.locale }
            copyOriginalIntoEditor={ this.props.copyOriginalIntoEditor }
            resetFailedChecks={ this.props.resetFailedChecks }
            resetSelectionContent={ this.props.resetSelectionContent }
            sendTranslation={ this.props.sendTranslation }
            updateTranslation={ this.props.updateTranslation }
            updateTranslationStatus={ this.props.updateTranslationStatus }
        />;
    }
}

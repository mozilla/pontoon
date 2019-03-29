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
    render() {
        const { entity } = this.props;

        if (!entity) {
            return null;
        }

        if (entity.format === 'ftl') {
            return <FluentEditor
                editor={ this.props.editor }
                translation={ this.props.translation }
                locale={ this.props.locale }
                copyOriginalIntoEditor={ this.props.copyOriginalIntoEditor }
                resetSelectionContent={ this.props.resetSelectionContent }
                sendTranslation={ this.props.sendTranslation }
                updateTranslation={ this.props.updateTranslation }
            />;
        }

        return <GenericEditor
            editor={ this.props.editor }
            translation={ this.props.translation }
            locale={ this.props.locale }
            copyOriginalIntoEditor={ this.props.copyOriginalIntoEditor }
            resetSelectionContent={ this.props.resetSelectionContent }
            sendTranslation={ this.props.sendTranslation }
            updateTranslation={ this.props.updateTranslation }
        />;
    }
}

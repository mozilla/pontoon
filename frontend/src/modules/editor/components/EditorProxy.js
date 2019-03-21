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
        const { editor, entity, translation, locale, updateTranslation, resetSelectionContent } = this.props;

        if (!entity) {
            return null;
        }

        if (entity.format === 'ftl') {
            return <FluentEditor
                editor={ editor }
                translation={ translation }
                locale={ locale }
                resetSelectionContent={ resetSelectionContent }
                updateTranslation={ updateTranslation }
            />;
        }

        return <GenericEditor
            editor={ editor }
            translation={ translation }
            locale={ locale }
            resetSelectionContent={ resetSelectionContent }
            updateTranslation={ updateTranslation }
        />;
    }
}

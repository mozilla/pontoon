/* @flow */

import * as React from 'react';

import * as editor from 'core/editor';

import SourceTranslationForm from './SourceTranslationForm';

import type { EditorProps } from 'core/editor';


type Props = {
    ...EditorProps,
    ftlSwitch: React.Node,
};


/**
 * Editor
 */
export default class SourceEditor extends React.Component<Props> {
    render() {
        const { ftlSwitch, ...props } = this.props;

        return <>
            <SourceTranslationForm { ...props } />
            <editor.EditorMenu
                { ...props }
                firstItemHook={ ftlSwitch }
            />
        </>;
    }
}

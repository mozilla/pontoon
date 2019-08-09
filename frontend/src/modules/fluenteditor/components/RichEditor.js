/* @flow */

import * as React from 'react';

import * as editor from 'core/editor';

import RichTranslationForm from './RichTranslationForm';

import type { EditorProps } from 'core/editor';


type Props = {
    ...EditorProps,
    ftlSwitch: React.Node,
};


/**
 * Editor for simple Fluent strings.
 */
export default class RichEditor extends React.Component<Props> {
    render() {
        const { ftlSwitch, ...props } = this.props;

        return <>
            <RichTranslationForm
                { ...props }
            />
            <editor.EditorMenu
                { ...props }
                firstItemHook={ ftlSwitch }
            />
        </>;
    }
}

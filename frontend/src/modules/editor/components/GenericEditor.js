/* @flow */

import * as React from 'react';

import type { Locale } from 'core/locales';


export type EditorProps = {|
    translation: string,
    locale: Locale,
    updateTranslation: Function,
|};


/*
 * Render a simple textarea to edit a translation.
 */
export default class GenericEditor extends React.Component<EditorProps> {
    handleChange = (event: SyntheticInputEvent<HTMLTextAreaElement>) => {
        this.props.updateTranslation(event.currentTarget.value);
    }

    render() {
        return <textarea
            value={ this.props.translation }
            onChange={ this.handleChange }
            dir={ this.props.locale.direction }
            lang={ this.props.locale.code }
            data-script={ this.props.locale.script }
        />;
    }
}

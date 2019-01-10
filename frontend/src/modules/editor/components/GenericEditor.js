/* @flow */

import * as React from 'react';


export type EditorProps = {|
    translation: string,
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
        />;
    }
}

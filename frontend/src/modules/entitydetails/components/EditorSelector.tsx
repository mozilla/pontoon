import * as React from 'react';

import './EditorSelector.css';

import { FluentEditor } from 'modules/fluenteditor';
import { GenericEditor } from 'modules/genericeditor';

type Props = {
    fileFormat: string;
};

export default function EditorSelector(
    props: Props,
): React.ReactElement<'div'> {
    if (props.fileFormat === 'ftl') {
        return (
            <div className='editor'>
                <FluentEditor />
            </div>
        );
    }
    return (
        <div className='editor'>
            <GenericEditor />
        </div>
    );
}

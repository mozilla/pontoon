/* @flow */

import * as React from 'react';

import './Term.css';

import type { TermType } from 'core/api';

type Props = {|
    term: TermType,
    isReadOnlyEditor: boolean,
    addTextToEditorTranslation: (string) => void,
|};


/**
 * Show term entry with its metadata.
 */
export default class Term extends React.Component<Props> {
    copyTermIntoEditor = (translation: string, event: SyntheticMouseEvent<HTMLLIElement>) => {
        if (this.props.isReadOnlyEditor) {
            return;
        }

        // Ignore if term not translated
        if (!translation) {
            return;
        }

        // Ignore if selecting text
        if (window.getSelection().toString()) {
            return;
        }

        this.props.addTextToEditorTranslation(translation);
    }

    render() {
        const { term, isReadOnlyEditor } = this.props;

        // Copying into the editor is not allowed
        const cannotCopy = (isReadOnlyEditor || !term.translation) ? 'cannot-copy' : '';

        return <li
            className={ `term ${cannotCopy}` }
            onClick={ (event) => this.copyTermIntoEditor(term.translation, event) }
        >
            <header>
                <span className='text'>{ term.text }</span>
                <span className='part-of-speech'>{ term.partOfSpeech }</span>
            </header>
            <p className='translation'>{ term.translation }</p>
            <p className='details'>
                <span className='definition'>{ term.definition }</span>
                <span className='divider'>&bull;</span>
                <span className='usage'>{ term.usage }</span>
            </p>
        </li>;
    }
}

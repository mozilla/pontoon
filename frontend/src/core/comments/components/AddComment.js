/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';
import { 
    Editor, 
    EditorState, 
    getDefaultKeyBinding, 
    convertToRaw,
    SelectionState,
    Modifier, 
} from 'draft-js';
import draftToHtml from 'draftjs-to-html';

import './AddComment.css';

import { UserAvatar } from 'core/user'

type Props = {|
    user: string,
    username: string,
    imageURL: string,
    translation?: ?number,
    addComment: (string, ?number) => void,
|};


export default function AddComments(props: Props) {
    const {
        user,
        username,
        imageURL,
        translation,
        addComment,
    } = props;

    let [editorState, setEditorState] = React.useState(
        EditorState.createEmpty()
    )
    const editor: any = React.useRef(null);

    React.useEffect(() => {
        focusEditor()
    }, []);

    if (!user) {
        return null;
    }
    
    const onChange = (editorState) => {
        setEditorState(editorState);
    }

    function focusEditor() {
        editor.current.focus();
    }

    function keyBindingFn(e: SyntheticKeyboardEvent<>) {
        if (e.keyCode === 13 && e.shiftKey === false) {
            return 'submit-on-enter'; 
        }
        
        return getDefaultKeyBinding(e)
    }

    const handleKeyCommand = (command: string) => {
        if (command === 'submit-on-enter') {
            submitComment();
            return 'handled';
        }
        return 'not-handled';
    }

    const clearEditorContent = () => {
        let contentState = editorState.getCurrentContent();
        const firstBlock = contentState.getFirstBlock();
        const lastBlock = contentState.getLastBlock();
        const allSelected = new SelectionState({
            anchorKey: firstBlock.getKey(),
            anchorOffset: 0,
            focusKey: lastBlock.getKey(),
            focusOffset: lastBlock.getLength(),
            hasFocus: true
        });
        contentState = Modifier.removeRange(contentState, allSelected, 'backward');
        editorState = EditorState.push(editorState, contentState, 'remove-range');
        editorState = EditorState.forceSelection(editorState, contentState.getSelectionAfter());
        setEditorState(editorState);
    }

    const submitComment = () => {
        if (!editorState.getCurrentContent().hasText()) {
            return null;
        }
        
        const rawContentState = convertToRaw(editorState.getCurrentContent());
        const comment = draftToHtml(
            rawContentState,
        )
        
        addComment(comment, translation);

        clearEditorContent();
    }

    return <div className='comment add-comment'>
        <UserAvatar
            username={ username }
            imageUrl={ imageURL }
        />
        <div className='container'>
            <div className='editor-wrapper' onClick={ focusEditor }>
                <Editor
                    ref={ editor }
                    editorState={ editorState }
                    placeholder='Write a comment…'
                    onChange={ onChange }
                    keyBindingFn={ keyBindingFn }
                    handleKeyCommand={ handleKeyCommand }
                />
            </div>
            <Localized
                id="comments-AddComment--submit-button"
                attrs={{ title: true }}
                glyph={
                    <i className="fa fa-paper-plane"></i>
                }
            >
                <button
                    className="submit-button"
                    title="Submit comment"
                    onClick={ submitComment }
                >
                    { '<glyph></glyph>' }
                </button>
            </Localized>
        </div>
    </div>
}

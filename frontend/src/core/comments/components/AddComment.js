/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';
import { Editor, EditorState, getDefaultKeyBinding } from 'draft-js';

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

    const [editorState, setEditorState] = React.useState(
        EditorState.createEmpty()
    )
    const editor: any = React.useRef(null);
    // const commentInput: any = React.useRef();
    // const minRows = 1;
    // const maxRows = 6;

   function focusEditor() {
        editor.current.focus();
    }

    function keyBindingFn(e: SyntheticKeyboardEvent<>) {
        if (e.keyCode === 13 && e.shiftKey === false) {
          return 'submitOnEnter' 
        }
      
        // This wasn't the delete key, so we return default for this key
        return getDefaultKeyBinding(e)
      }

    React.useEffect(() => {
        focusEditor()
    }, []);

    // const handleOnChange = () => {
    //     const textAreaLineHeight = 24;
    //     commentInput.current.rows = minRows;

    //     const currentRows = Math.trunc(commentInput.current.scrollHeight / textAreaLineHeight);

    //     if (currentRows < maxRows) {
    //         commentInput.current.rows = currentRows;
    //     }
    //     else {
    //         commentInput.current.rows = maxRows;
    //     }
    // }

    // const handleOnKeyDown = (event: SyntheticKeyboardEvent<>) => {
    //     if (event.keyCode === 13 && event.shiftKey === false) {
    //         submitComment(event);
    //     }
    // }

    const handleKeyCommand = (command: string) => {
        if (command === 'submitOnEnter') {
            submitComment();
          return 'handled';
        }
        return 'not-handled';
      }

      const submitComment = () => {
          console.log("Submit on enter worked.");
      }

    // const submitComment = (event: SyntheticEvent<>) => {
    //     event.preventDefault();
    //     const comment = '';
    //     const contentState = editorState.getCurrentContent();
    //     console.log('content state', contentState);

    //     if (!comment) {
    //         return null;
    //     }

    //     addComment(comment, translation);

    //     setEditorState(EditorState.createEmpty());
    // };

    if (!user) {
        return null;
    }

    return <div className='comment add-comment'>
        <UserAvatar
            username={ username }
            imageUrl={ imageURL }
        />
        <div className='container'>
            <div className='comment-div' onClick={ focusEditor }>
                <Editor
                    ref={editor}
                    editorState={editorState}
                    placeholder='Write a comment…'
                    onChange={editorState => setEditorState(editorState)}
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
        {/* <form className='container'>
            <Localized
                id='comments-AddComment--input'
                attrs={{ placeholder: true }}
            >
                <textarea
                    autoFocus
                    name='comment'
                    dir='auto'
                    placeholder={ `Write a comment…` }
                    rows={ minRows }
                    ref={ commentInput }
                    onChange={ handleOnChange }
                    onKeyDown={ handleOnKeyDown }
                />
            </Localized>
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
        </form> */}
    </div>
}

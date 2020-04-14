/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';
import Editor from 'draft-js-plugins-editor';
import { 
    EditorState, 
    getDefaultKeyBinding, 
    convertToRaw,
    SelectionState,
    Modifier, 
} from 'draft-js';
import draftToHtml from 'draftjs-to-html';
import createLinkifyPlugin from 'draft-js-linkify-plugin';
import createMentionPlugin, { defaultSuggestionsFilter } from 'draft-js-mention-plugin';

import './AddComment.css';
import 'draft-js/dist/Draft.css';
import 'draft-js-linkify-plugin/lib/plugin.css';


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

    const mentions = [
        {
          name: 'Matthew Russell',
          link: 'https://twitter.com/mrussell247',
          avatar: 'https://pbs.twimg.com/profile_images/517863945/mattsailing_400x400.jpg',
        },
        {
          name: 'Julian Krispel-Samsel',
          link: 'https://twitter.com/juliandoesstuff',
          avatar: 'https://avatars2.githubusercontent.com/u/1188186?v=3&s=400',
        },
    ]

    let [editorState, setEditorState] = React.useState(
        EditorState.createEmpty()
    )
    const [suggestions, setSuggestions] = React.useState(mentions)
    const editor: any = React.useRef(null);

    // This is a temporary workaround to keep the editor from clearing the 
    // decorators set for the plugins
    React.useEffect(() => {
        setTimeout(() => {
            focusEditor()
        }, 0);
    }, []);

    if (!user) {
        return null;
    }

    const linkifyPlugin = createLinkifyPlugin({ target: '_blank' });
    const mentionPlugin = createMentionPlugin();
    const { MentionSuggestions } = mentionPlugin; 

    const plugins = [mentionPlugin, linkifyPlugin];

    const onChange = (editorState) => {
        setEditorState(editorState);
    }

    const onSearchChange = ({ value }) => {
        setSuggestions(defaultSuggestionsFilter(value, mentions))
    };

    const onAddMention = () => { 
        // get the mention object selected
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

    // TODO: Would like to find another solution or refactor this as it is not very pretty
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
                <Localized
                    id='comments-AddComment--input'
                    attrs={{ placeholder: true }}
                >
                    <Editor
                        ref={ editor }
                        editorState={ editorState }
                        placeholder='Write a comment…'
                        onChange={ onChange }
                        plugins={ plugins }
                        keyBindingFn={ keyBindingFn }
                        handleKeyCommand={ handleKeyCommand }
                    />
                </Localized>
                    <MentionSuggestions
                        onSearchChange={ onSearchChange }
                        suggestions={ suggestions }
                        onAddMention ={ onAddMention }
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

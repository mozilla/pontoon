/* @flow */

import * as React from 'react';
import ReactDOM from 'react-dom';
import { Localized } from '@fluent/react';
import { 
    Editor, 
    Transforms, 
    Range, 
    createEditor, 
    Text,
    Node,
} from 'slate';
import { 
    Slate, 
    Editable, 
    ReactEditor, 
    withReact,
} from 'slate-react';
import escapeHtml from 'escape-html'

import './AddComment.css';

import { UserAvatar } from 'core/user'

import type { NavigationParams } from 'core/navigation';
import type { TextType, MentionType, InitialType, UsersType } from 'core/api';

type Props = {|
    user: string,
    username: string,
    imageURL: string,
    parameters: ?NavigationParams,
    translation?: ?number,
    projectManager?: Object,
    users: Array<UsersType>,
    addComment: (string, ?number) => void,
    getUsers: () => void,
|};


export default function AddComments(props: Props) {
    const {
        user,
        username,
        imageURL,
        parameters,
        translation,
        projectManager,
        users,
        addComment,
        getUsers,
    } = props;

    if (projectManager) { console.log(projectManager); }
    console.log(users);
    
    

    const initialValue = [{ type: 'paragraph', children: [{ text: '' }] }];
    /**
     * TODO: This works to add the mention of the PM, but it clears as soon as another char is typed.
     * Focus is being placed at the beginning instead of the end which could be the reason
     * Also, this breaks when opening comment tab directly - maybe inserting a node instead of setting state??
     */ 
    
    // const insertProjectManager = (projectManager) => {
    //     return [{ type: 'mention', character: projectManager.contact, url: `mailto:${projectManager.email}`, children: [{ text: projectManager.contact }, { text: ' ' }]}];
    // }

    const ref: any = React.useRef();
    // TODO: Make this conditional on if project Manager then call insertProjectManater ???? - this approach breaks the initial value
    const [value, setValue] = React.useState(initialValue);
    const [target, setTarget] = React.useState();
    const [index, setIndex] = React.useState(0);
    const [search, setSearch] = React.useState('');
    const renderElement = React.useCallback(props => <Element {...props} />, []);
    const editor = React.useMemo(
        () => withMentions(withReact(createEditor())), []
    );

    const allUsers = users;
    const USERS = allUsers.map(user => user.name);
    const chars = USERS.filter(c =>
        c.toLowerCase().startsWith(search.toLowerCase())
    ).slice(0, 10);

    React.useEffect(() => {
        if (target && chars.length > 0) {
            const el = ref.current;
            const domRange = ReactEditor.toDOMRange(editor, target);
            const rect = domRange.getBoundingClientRect();

            // If suggestions overflow the window height then adjust the
            // position so they display above the comment
            const suggestionsHeight = el.clientHeight + 10;
            let setTop = rect.top + window.pageYOffset;
            
            if (setTop + suggestionsHeight > window.innerHeight) { 
                setTop -= suggestionsHeight;
            }
            else {
                setTop += 24;
            }
            el.style.top = `${setTop}px`;
            el.style.left = `${rect.left + window.pageXOffset}px`;
        }
    }, [chars.length, editor, index, search, target]);

    const mentionsKeyDown = React.useCallback(
        event => {
            if (target) {
                switch (event.key) {
                    case 'ArrowDown': {
                        event.preventDefault();
                        const prevIndex = index >= chars.length - 1 ? 0 : index + 1;
                        setIndex(prevIndex);
                        break;
                    }
                    case 'ArrowUp': {
                        event.preventDefault();
                        const nextIndex = index <= 0 ? chars.length - 1 : index - 1;
                        setIndex(nextIndex);
                        break;
                    }
                    case 'Tab':
                    case 'Enter':
                        event.preventDefault();
                        Transforms.select(editor, target);
                        insertMention(editor, chars[index], users);
                        setTarget(null);
                        break;
                    case 'Escape':
                        event.preventDefault();
                        setTarget(null);
                        break;
                    default:
                        return;
                }
            }
        },
        [chars, editor, index, target, users]
    );

    const onKeyDown = (event: SyntheticKeyboardEvent<>) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            submitComment();
        }
        if (event.key === 'Enter' && event.shiftKey) { 
            event.preventDefault();
            /*
            * This allows for the new lines to render while adding comments.
            * To avoid an issue with the cursor placement and an error when 
            * navigating with arrows that occurs in Firefox '\n' can't be 
            * the last character so the BOM was added
            */
            editor.insertText('\n\uFEFF');
            return null;
        }
    }
    
    if (!user) {
        return null;
    }

    const onChange = (value) => {
        setValue(value);
        const { selection } = editor;

        if (selection && Range.isCollapsed(selection)) {
            const [start] = Range.edges(selection);
            const wordBefore = Editor.before(editor, start, { unit: 'word' });
            const before = wordBefore && Editor.before(editor, wordBefore);
            const beforeRange = before && Editor.range(editor, before, start);
            const beforeText = beforeRange && Editor.string(editor, beforeRange);
            const beforeMatch = beforeText && beforeText.match(/^@(\w+)$/);
            const after = Editor.after(editor, start);
            const afterRange = Editor.range(editor, start, after);
            const afterText = Editor.string(editor, afterRange);
            const afterMatch = afterText.match(/^(\s|$)/);

            if (beforeMatch) { getUsers() }

            if (beforeMatch && afterMatch) {
                setTarget(beforeRange);
                setSearch(beforeMatch[1]);
                setIndex(0);
                return;
            }
        }
    
        setTarget(null);
    }

    const Portal = ({ children }) => {
        if (!document.body) {
            return null;
        }
        return ReactDOM.createPortal(children, document.body);
    }

    const serialize = (node: TextType | MentionType | InitialType) => {
        if (Text.isText(node) && node.text) {
            return escapeHtml(node.text);
        }

        if (!node.type  || !node.children) {
            return;
        }

        const children = node.children.map(n => serialize(n)).join('');

        switch (node.type) {
            case 'paragraph':
                return `<p>${children.trim()}</p>`;
            case 'mention':
                if (node.url) {
                    return `<a href="${escapeHtml(node.url)}">${children}</a>`;
                }
                break;
            default:
                return children;
        }
    };

    const submitComment = () => {
        if (Node.string(editor).trim() === '') {
            return null;
        }
        
        const comment = value.map(node => serialize(node)).join('');

        addComment(comment, translation);

        Transforms.select(
            editor, { anchor: { path: [0,0], offset: 0 }, focus: { path: [0,0], offset: 0 } }
        );
        setValue(initialValue);
    };

    return <div className='comment add-comment'>
        <UserAvatar
            username={ username }
            imageUrl={ imageURL }
        />
        <div className='container'>
            <Slate  editor={ editor }  value={ value } onChange={ onChange }>
                <Localized
                    id='comments-AddComment--input'
                    attrs={{ placeholder: true }}
                >
                    <Editable 
                        className='comment-editor'
                        autoFocus
                        name='comment'
                        dir='auto' 
                        placeholder={ `Write a comment…` }
                        renderElement={ renderElement }
                        onKeyDown={ target ? mentionsKeyDown : onKeyDown }
                    />
                </Localized>
                {target && chars.length > 0 && (
                    <Portal>
                        <div
                            ref={ref}
                            className='mention-list'
                        >
                            {chars.map((char, i) => (
                                <div
                                    key={char}
                                    className={ i === index ? 'mention active-mention' : 'mention' }
                                >
                                    {char}
                                </div>
                            ))}
                        </div>
                    </Portal>
                )}
            </Slate>
            <Localized
                id="comments-AddComment--submit-button"
                attrs={{ title: true }}
                elems={{ glyph: <i className="fa fa-paper-plane" /> }}
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

const withMentions = (editor) => {
    const { isInline, isVoid } = editor;
  
    editor.isInline = element => {
        return element.type === 'mention' ? true : isInline(element);
    }
  
    editor.isVoid = element => {
        return element.type === 'mention' ? true : isVoid(element);
    }
  
    return editor
};
  
const insertMention = (editor, character, users) => {
    const selectedUser = users.filter(user => user.name === character);
    const userUrl = selectedUser[0].url;
    const display = selectedUser[0].display;
    const mention = { type: 'mention', character, url: userUrl, children: [{ text: display }] };
    Transforms.insertNodes(editor, mention);
    Transforms.move(editor);
};

const Element = (props) => {
    const { attributes, children, element } = props;
        switch (element.type) {
        case 'mention':
            return <MentionElement {...props} />;
        default:
            return <p {...attributes}>{children}</p>;
    }
};

const MentionElement = ({ attributes, children, element }) => {
    return (
        <span
            {...attributes}
            contentEditable={false}
            className='mention-element'
        >
            @{element.character}
            {children}
        </span>
    )
};

// const users = [
//     { 
//         'name': 'Matjaz',
//         'url': 'https://matjaz.com',
//         'display': 'mathjazz'
//     },
//     { 
//         'name': 'Adrian',
//         'url': 'https://adrian.com',
//         'display': 'adngdb'
//     },
//     { 
//         'name': "Jotes",
//         'url': 'https://jotes.com',
//         'display': 'jotes',
//     },
//     { 
//         'name': 'April',
//         'url': 'https://april.com',
//         'display': 'abowler', 
//     },
// ];

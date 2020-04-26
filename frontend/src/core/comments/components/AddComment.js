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

type Props = {|
    user: string,
    username: string,
    imageURL: string,
    parameters: ?NavigationParams,
    translation?: ?number,
    addComment: (string, ?number) => void,
|};


export default function AddComments(props: Props) {
    const {
        user,
        username,
        imageURL,
        parameters,
        translation,
        addComment,
    } = props;

    const initialValue = [{ type: 'paragraph', children: [{ text: '' }] }];

    const ref: any = React.useRef();
    const [value, setValue] = React.useState(initialValue);
    const [target, setTarget] = React.useState();
    const [index, setIndex] = React.useState(0);
    const [search, setSearch] = React.useState('');
    const renderElement = React.useCallback(props => <Element {...props} />, []);
    const editor = React.useMemo(
        () => withMentions(withReact(createEditor())), []
    );

    const chars = USERS.filter(c =>
        c.toLowerCase().startsWith(search.toLowerCase())
    ).slice(0, 10);

    React.useEffect(() => {
        if (target && chars.length > 0) {
            const el = ref.current
            const domRange = ReactEditor.toDOMRange(editor, target)
            const rect = domRange.getBoundingClientRect()
            el.style.top = `${rect.top + window.pageYOffset + 24}px`
            el.style.left = `${rect.left + window.pageXOffset}px`
        }
    }, [chars.length, editor, index, search, target]);

    const onKeyDown = React.useCallback(
        event => {
            if (target) {
                switch (event.key) {
                    case 'ArrowDown':
                        event.preventDefault()
                        const prevIndex = index >= chars.length - 1 ? 0 : index + 1
                        setIndex(prevIndex)
                        break
                    case 'ArrowUp':
                        event.preventDefault()
                        const nextIndex = index <= 0 ? chars.length - 1 : index - 1
                        setIndex(nextIndex)
                        break
                    case 'Tab':
                    case 'Enter':
                        event.preventDefault()
                        Transforms.select(editor, target)
                        insertMention(editor, chars[index])
                        setTarget(null)
                        break
                    case 'Escape':
                        event.preventDefault()
                        setTarget(null)
                        break
                    default:
                        return
                }
            }
        },
        // Look into how to avoid issues re: 'char' and 'editor' not being present
        // eslint-disable-next-line 
        [index, search, target]
    );
    
    if (!user) {
        return null;
    }

    const onChange = (value) => {
        setValue(value)
        const { selection } = editor

        if (selection && Range.isCollapsed(selection)) {
            const [start] = Range.edges(selection)
            const wordBefore = Editor.before(editor, start, { unit: 'word' })
            const before = wordBefore && Editor.before(editor, wordBefore)
            const beforeRange = before && Editor.range(editor, before, start)
            const beforeText = beforeRange && Editor.string(editor, beforeRange)
            const beforeMatch = beforeText && beforeText.match(/^@(\w+)$/)
            const after = Editor.after(editor, start)
            const afterRange = Editor.range(editor, start, after)
            const afterText = Editor.string(editor, afterRange)
            const afterMatch = afterText.match(/^(\s|$)/)
    
            if (beforeMatch && afterMatch) {
                setTarget(beforeRange)
                setSearch(beforeMatch[1])
                setIndex(0)
                return
            }
        }
    
        setTarget(null)
    }

    const Portal = ({ children }) => {
        return ReactDOM.createPortal(children, document.body)
    }

    const serialize = (value) => {
        if (Text.isText(value)) {
            return escapeHtml(value.text)
        }

        const children = value.children.map(v => serialize(v)).join('');

        switch (value.type) {
            case 'paragraph':
                return `<p>${children}</p>`
            case 'link':
                return `<a href="${escapeHtml(value.url)}">${children}</a>`
            case 'mention':
                return `<a href="${escapeHtml(value.url)}">${children}</a>`
            default:
                return children
        }
    };

    const submitComment = () => {
        // TODO: work out how to prevent empty comments when only 'enter' is pressed
        if (value.length <= 1 && Node.string(value[0]).length === 0) {
            return null;
        }

        const comment = serialize(value[0]);

        addComment(comment, translation);

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
                        onKeyDown={ onKeyDown }
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

const withMentions = editor => {
    const { isInline, isVoid } = editor
  
    editor.isInline = element => {
        return element.type === 'mention' ? true : isInline(element)
    }
  
    editor.isVoid = element => {
        return element.type === 'mention' ? true : isVoid(element)
    }
  
    return editor
};
  
const insertMention = (editor, character) => {
    const selectedUser = users.filter(user => user.name === character);
    const userUrl = selectedUser[0].url;
    const display = selectedUser[0].display;
    const mention = { type: 'mention', character, url: userUrl, children: [{ text: display }] }
    Transforms.insertNodes(editor, mention)
    Transforms.move(editor)
};
  
const Element = props => {
    const { attributes, children, element } = props
        switch (element.type) {
        case 'mention':
            return <MentionElement {...props} />
        default:
            return <p {...attributes}>{children}</p>
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

const users = [
    { 
        'name': 'Matjaz',
        'url': 'https://matjaz.com',
        'display': 'mathjazz'
    },
    { 
        'name': 'Adrian',
        'url': 'https://adrian.com',
        'display': 'adngdb'
    },
    { 
        'name': "Jotes",
        'url': 'https://jotes.com',
        'display': 'jotes',
    },
    { 
        'name': 'April',
        'url': 'https://april.com',
        'display': 'abowler', 
    },
];

const USERS = users.map(user => user.name);

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

import type { CommentState } from 'core/comments';
import type { NavigationParams } from 'core/navigation';
import type { TextType, MentionType, InitialType } from 'core/api';
import { TeamComments } from 'modules/teamcomments';

type Props = {|
    user: string,
    username: string,
    imageURL: string,
    parameters: ?NavigationParams,
    translation?: ?number,
    users: CommentState,
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
        users,
        addComment,
        getUsers,
    } = props;

    const initialValue = [{ type: 'paragraph', children: [{ text: '' }] }];
       
    const ref: any = React.useRef();
    const [target, setTarget] = React.useState();
    const [index, setIndex] = React.useState(0);
    const [search, setSearch] = React.useState('');
    const [scrollPosition, setScrollPosition] = React.useState(0);
    const renderElement = React.useCallback(props => <Element {...props} />, []);
    const editor = React.useMemo(
        () => withMentions(withReact(createEditor())), []
    );
    const [value, setValue] = React.useState(initialValue);

    // Set focus on Editor
    React.useEffect(() => {
        ReactEditor.focus(editor);
        Transforms.select(editor, Editor.end(editor, []));
    }, [editor])
    
    React.useEffect(() => {
        getUsers();
    }, [getUsers])

    const usersList = users.users;
    const USERS = usersList.map(user => user.name);
    const chars = USERS.filter(c =>
        c.toLowerCase().startsWith(search.toLowerCase())
    ).slice(0, 10);

    React.useLayoutEffect(() => {
        if (target && chars.length > 0) {
            const el = ref.current;
            const domRange = ReactEditor.toDOMRange(editor, target);
            const rect = domRange.getBoundingClientRect();
            const teamsContainer = document.querySelector('.react-tabs');
            const teamsRect = teamsContainer ? teamsContainer.getBoundingClientRect() : null;

            let setTop = (rect.top + window.pageYOffset) + 21;
            let setLeft = rect.left + window.pageXOffset;

            // If suggestions overflow the window or teams container height then adjust the
            // position so they display above the comment
            const suggestionsHeight = el.clientHeight + 10;
            const teamsOverflow = teamsRect ? setTop + suggestionsHeight > teamsRect.height : false;
            if (setTop + suggestionsHeight > window.innerHeight || teamsOverflow) { 
                setTop = (setTop - suggestionsHeight) - 21;
            }

            // If suggestions scroll below the next section then hide the suggestions
            const parent = document.querySelector('.team-comments');
            const teamCommentsActive = parent ? parent.contains(document.activeElement) : false;
            if (teamCommentsActive && (setTop - 21) > teamsRect.height) {
                el.style.display = 'none';
            }
            
            // If suggestions overflow the window width then adjust the
            // position so they display to the left of the mention
            const suggestionsWidth = el.clientWidth
            if (setLeft + suggestionsWidth > window.innerWidth) {
                setLeft = rect.right - suggestionsWidth;
            }

            el.style.top = `${setTop}px`;
            el.style.left = `${setLeft}px`;
        }
    }, [chars.length, editor, index, search, target, scrollPosition]);

    React.useEffect(() => {
        // $FLOW_IGNORE
        const handleScroll = (e: SyntheticEvent<HTMLElement>) => {
            const element = e.currentTarget;
            setScrollPosition(element.scrollTop);
        }
        const historyScroll = document.querySelector('#historyUl');
        const teamsScroll = document.querySelector('#react-tabs-3');
        if (!historyScroll && !teamsScroll) {
            return;
        }

        // $FLOW_IGNORE
        historyScroll.addEventListener('scroll', handleScroll);
        // $FLOW_IGNORE
        teamsScroll.addEventListener('scroll', handleScroll);

        return () => {
            // $FLOW_IGNORE
            historyScroll.removeEventListener('scroll', handleScroll);
            // $FLOW_IGNORE
            teamsScroll.removeEventListener('scroll', handleScroll);
        }
    }, [])

    const mentionsKeyDown = React.useCallback(
        (event) => {
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
                        insertMention(editor, chars[index], usersList);
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
        [chars, editor, index, target, usersList]
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

    const handleOnChange = (value) => {
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
            <Slate  editor={ editor }  value={ value } onChange={ handleOnChange }>
                <Localized
                    id='comments-AddComment--input'
                    attrs={{ placeholder: true }}
                >
                    <Editable 
                        className='comment-editor'
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
  
    editor.isInline = (element) => {
        return element.type === 'mention' ? true : isInline(element);
    }
  
    editor.isVoid = (element) => {
        return element.type === 'mention' ? true : isVoid(element);
    }
  
    return editor;
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

/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';
import { createEditor, Text } from 'slate';
import { Slate, Editable, withReact } from 'slate-react';
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

    const blankSlateValue = [{ type:"paragraph", children: [{ text: '' }] }];

    const editor = React.useMemo(() => withReact(createEditor()), []);
    const [value, setValue] = React.useState(blankSlateValue);

    if (!user) {
        return null;
    }



    // TODO:  This is not working as written. It is saying 'value' is undefined
    const serialize = (value) => {
        if (Text.isText(value)) {
            return escapeHtml(value.text);
        }

        const children = value[0].children.map(n => serialize(n)).join('');

        switch (value.type) {
            case 'link':
                return `<a href="${escapeHtml(node.url)}>${children}</a>`
            default:
                return `<p>${children}</p>`
        }
    }

    // TODO:  Fix onKeyDown as it submits but crashes the app
    // const handleOnKeyDown = (event: SyntheticKeyboardEvent<>) => {
    //     if (event.keyCode === 13 && event.shiftKey === false) {
    //         event.preventDefault();
    //         submitComment(event);
    //     }
    // }

    const submitComment = (event: SyntheticEvent<>) => {
        event.preventDefault();
        const comment = serialize(value);

        if (!comment) {
            return null;
        }

        addComment(comment, translation);

        setValue(blankSlateValue);
    };

    return <div className='comment add-comment'>
        <UserAvatar
            username={ username }
            imageUrl={ imageURL }
        />
        <div className='container'>
            <Slate editor={editor} value={value} onChange={value => setValue(value)}>
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
                        // onKeyDown={ handleOnKeyDown}
                    />
                </Localized>
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
                    // onClick={ clearEditor }
                >
                    { '<glyph></glyph>' }
                </button>
            </Localized>
        </div>
    </div>
}

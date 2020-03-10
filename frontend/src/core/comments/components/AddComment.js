/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';
import { MentionsInput, Mention } from 'react-mentions';

import './AddComment.css';

import { UserAvatar } from 'core/user'

type Props = {|
    user: string,
    username: string,
    imageURL: string,
    translation?: ?number,
    projectManager?: Object,
    addComment: (string, ?number) => void,
    getUsers: () => void,
|};


export default function AddComments(props: Props) {
    const {
        user,
        username,
        imageURL,
        translation,
        addComment,
        getUsers,
        projectManager,
    } = props;

    const commentInput: any = React.useRef();
    const [value, setValue] = React.useState('');

    const handleOnChange = React.useCallback((_, newValue) => setValue(newValue), [setValue])

    const handleOnKeyDown = (event: SyntheticKeyboardEvent<>) => {
        if (event.keyCode === 13 && event.shiftKey === false) {
            event.preventDefault();
            submitComment(event);
        }
    }

    const handleOnKeyDown = (event: SyntheticKeyboardEvent<>) => {
        if (event.keyCode === 13 && event.shiftKey === false) {
            submitComment(event);
        }
    }

    const submitComment = (event: SyntheticEvent<>) => {
        event.preventDefault();
        const comment = commentInput.current.value;

        if (!comment) {
            return null;
        }

        addComment(comment, translation);

        setValue('');
    };

    if (!user) {
        return null;
    }
    

    return <div className='comment add-comment'>
        <UserAvatar
            username={ username }
            imageUrl={ imageURL }
        />
        <form className='container'>
            <Localized
                id='comments-AddComment--input'
                attrs={{ placeholder: true }}
            >
                <MentionsInput
                    className='mentions'
                    autoFocus
                    value={ value }
                    dir='auto'
                    placeholder={ `Write a comment…` }
                    markup="@[__display__](__type__:__id__)"
                    onChange={ handleOnChange }
                    onKeyDown={ handleOnKeyDown }
                >
                    <Mention
                        className='mentions__mention'
                        trigger="@"
                        data={ getUsers }
                        appendSpaceOnAdd='true'
                    />
                </MentionsInput>
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
        </form>
    </div>
}

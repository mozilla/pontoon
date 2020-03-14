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

    const [value, setValue] = React.useState('');

    const handleOnChange = React.useCallback((_, newValue) => setValue(newValue), [setValue])

    const handleOnKeyDown = (event: SyntheticKeyboardEvent<>) => {
        if (event.keyCode === 13 && event.shiftKey === false) {
            event.preventDefault();
            submitComment(event);
        }
    }

    const submitComment = (event: SyntheticEvent<>) => {
        event.preventDefault();
        const comment = value;

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
                    onChange={ handleOnChange }
                    onKeyDown={ handleOnKeyDown }
                >
                    <Mention
                        className='mentions__mention'
                        trigger='@'
                        markup='@[__display__](__id__)'
                        data={[
                            { display: 'abowler2@gmail.com', id: 'abowler2@gmail.com' }, 
                            { display: 'adrian@mozilla.com', id: 'adrian@mozilla.com' }, 
                            { display: 'matjaz@mozilla.com', id: 'matjaz@mozilla.com' },
                        ]}
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

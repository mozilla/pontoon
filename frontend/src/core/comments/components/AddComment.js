/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './Comment.css';

import { UserAvatar } from 'core/user'

type Props = {|
    user: string,
    username: string,
    imageURL: string,
|};


export default function AddComments(props: Props) {
    const { user, username, imageURL } = props;

    if (!user) {
        return null;
    }

    const submit_comment = (event: SyntheticMouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
        console.log('Comment');
    };

    const reject_with_comment = (event: SyntheticMouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
        console.log('Reject');
    };

    const approve_with_comment = (event: SyntheticMouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
        console.log('Approve');
    };

    return <div className='comment add-comment'>
        <UserAvatar
            user={ user }
            username={ username }
            title=''
            imageUrl={ imageURL }
        />
        <form className='container'>
            <div className='content'>
                <Localized
                    id='comments-AddComment--input'
                    attrs={{ placeholder: true }}
                >
                    <input
                        type='text'
                        id='comment-input'
                        name='comment'
                        placeholder={'Write a comment...'}
                    ></input>
                </Localized>
            </div>
            <div className='options'>
                <Localized id='comments-AddComment--comment-button'>
                    <button
                        className='comment-btn'
                        onClick={ (e) => submit_comment(e) }
                    >
                        Comment
                    </button>
                </Localized>
                <Localized id='comments-AddComment--reject-button'>
                    <button
                        className='btn'
                        onClick={ (e) => reject_with_comment(e) }
                    >
                        Reject & Comment
                    </button>
                </Localized>
                <Localized id='comments-AddComment--approve-button'>
                    <button
                        className='btn'
                        onClick={ (e) => approve_with_comment(e) }
                    >
                        Approve & Comment
                    </button>
                </Localized>
            </div>
        </form>
    </div>
}

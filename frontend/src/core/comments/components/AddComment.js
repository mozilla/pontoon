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

    const submitComment = (event: SyntheticMouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
        let comment=document.querySelector('#comment-input').value
        document.getElementById('comment-input').value = ''
        console.log(comment);
    };

    const rejectWithComment = (event: SyntheticMouseEvent<HTMLButtonElement>) => {
        event.preventDefault();
        console.log('Reject');
    };

    const approveWithComment = (event: SyntheticMouseEvent<HTMLButtonElement>) => {
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
                    />
                </Localized>
            </div>
            <div className='options'>
                <Localized id='comments-AddComment--comment-button'>
                    <button
                        className='comment-btn'
                        onClick={ (e) => submitComment(e) }
                    >
                        Comment
                    </button>
                </Localized>
                <Localized id='comments-AddComment--reject-button'>
                    <button
                        className='btn'
                        onClick={ (e) => rejectWithComment(e) }
                    >
                        Reject & Comment
                    </button>
                </Localized>
                <Localized id='comments-AddComment--approve-button'>
                    <button
                        className='btn'
                        onClick={ (e) => approveWithComment(e) }
                    >
                        Approve & Comment
                    </button>
                </Localized>
            </div>
        </form>
    </div>
}

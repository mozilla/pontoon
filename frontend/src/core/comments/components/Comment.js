/* @flow */

import * as React from 'react';
import ReactTimeAgo from 'react-time-ago';

import type { TranslationComment } from 'core/api';

import { UserImage } from 'core/user'


type Props = {|
    comment: TranslationComment,
|};


export default function Comment(props: Props) {
    const { comment } = props;

    function renderUser() {
        return <a
            href={ `/contributors/${comment.username}` }
            title='Author'
            target='_blank'
            rel='noopener noreferrer'
            onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
        >
            { comment.author }
        </a>
    }

    if (!comment) {
            return null;
    }

    return <div>
        <div title='Comment'>
            <UserImage
                user={ comment.author }
                username={ comment.username }
                title= 'Author'
                imageUrl={ comment.userGravatarUrlSmall }
            />
            { renderUser() }
            { comment.content }
            <div>
                <ReactTimeAgo
                    dir='ltr'
                    date={ new Date(comment.dateIso) }
                    title={ `${comment.createdAt} UTC` }
                />
            </div>
        </div>
    </div>
}

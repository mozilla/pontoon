/* @flow */

import * as React from 'react';
import ReactTimeAgo from 'react-time-ago';

import type { TranslationComment } from 'core/api';

import { UserAvatar } from 'core/user'


type Props = {|
    comment: TranslationComment,
|};


export default function Comment(props: Props) {
    const { comment } = props;

    if (!comment) {
            return null;
    }

    return <div>
        <UserAvatar
            user={ comment.author }
            username={ comment.username }
            title= ''
            imageUrl={ comment.userGravatarUrlSmall }
        />
        <a
            href={ `/contributors/${comment.username}` }
            target='_blank'
            rel='noopener noreferrer'
            onClick={ (e: SyntheticMouseEvent<>) => e.stopPropagation() }
        >
            { comment.author }
        </a>
        { comment.content }
        <div>
            <ReactTimeAgo
                dir='ltr'
                date={ new Date(comment.dateIso) }
                title={ `${comment.createdAt} UTC` }
            />
        </div>
    </div>
}

/* @flow */

import * as React from 'react';
import ReactTimeAgo from 'react-time-ago';
import { Localized } from '@fluent/react';

import './CommentsSummary.css';

import { UserAvatar } from 'core/user';


type Props = {|
    comments: Array<Object>,
    areCommentsVisible: boolean,
    setCommentsVisibility: (boolean) => void,
|};


export default function CommentsSummary(props: Props) {
    const { comments, areCommentsVisible, setCommentsVisibility } = props;
    const commentCount = comments.length;

    const authors = [...new Set(comments.map(comment => comment.username))];
    const lastComment = [...comments].pop();

    function toggleComments() {
        setCommentsVisibility(!areCommentsVisible);
    }

    return <div
        className='comments-summary'
        onClick={ toggleComments }
        title=''
    >
        { commentCount ? <ul>
            { authors.map((author, index) => {
                const comment = comments.filter(comment => (comment.username === author))[0];
                return <li key={ index }>
                    <UserAvatar
                        username={ author }
                        imageUrl={ comment.userGravatarUrlSmall }
                    />
                </li>; }) }
            </ul>
            :
            <i className='no-avatars fas fa-comment' />
        }

        <Localized
            id='history-Translation--comment-summary-count'
            $commentCount={ commentCount }
        >
            <span className='count'>
                { `${commentCount} Comments` }
            </span>
        </Localized>

        { !lastComment ? null :
            <Localized
                id='history-Translation--comment-summary-last-commented'
                timeago={
                    <ReactTimeAgo
                        dir='ltr'
                        date={ new Date(lastComment.dateIso) }
                        title={ `${lastComment.createdAt} UTC` }
                    />
                }
            >
                <span className='last-commented'>{ 'Last commented <timeago></timeago>' }</span>
            </Localized>
        }

        { !areCommentsVisible ?
            <Localized
                id='history-Translation--comment-summary-expand-comments'
                glyph={
                    <i className="fa fa-chevron-down fa-lg" />
                }
            >
                <span className='toggle-comments'>{ 'Expand comments <glyph></glyph>' }</span>
            </Localized>
            :
            <Localized
                id='history-Translation--comment-summary-collapse-comments'
                glyph={
                    <i className="fa fa-chevron-up fa-lg" />
                }
            >
                <span className='toggle-comments'>{ 'Collapse comments <glyph></glyph>' }</span>
            </Localized>
        }
    </div>;
}

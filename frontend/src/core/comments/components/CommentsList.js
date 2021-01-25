/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './CommentsList.css';

import { Comment, AddComment } from 'core/comments';

import type { NavigationParams } from 'core/navigation';
import type { TranslationComment } from 'core/api';
import type { UserState } from 'core/user';
import type { HistoryTranslation } from 'modules/history';

type Props = {|
    comments: Array<TranslationComment>,
    parameters?: NavigationParams,
    translation?: HistoryTranslation,
    user: UserState,
    users: UserState,
    contactPerson?: string,
    canComment: boolean,
    canPin?: boolean,
    addComment: (string, ?number) => void,
    togglePinnedStatus?: (boolean, number) => void,
    resetContactPerson?: () => void,
|};

export default function CommentsList(props: Props) {
    const {
        comments,
        parameters,
        translation,
        user,
        canComment,
        canPin,
        addComment,
        users,
        togglePinnedStatus,
        contactPerson,
        resetContactPerson,
    } = props;

    const translationId = translation ? translation.pk : null;

    // rendering comment
    const renderComment = (comment) => {
        return (
            <Comment
                comment={comment}
                canPin={canPin}
                key={comment.id}
                togglePinnedStatus={togglePinnedStatus}
            />
        );
    };

    const pinnedComments = comments.filter((comment) => comment.pinned);

    return (
        <div className='comments-list'>
            {pinnedComments.length ? (
                <section className='pinned-comments'>
                    <Localized id='comments-CommentsList--pinned-comments'>
                        <h2 className='title'>PINNED COMMENTS</h2>
                    </Localized>

                    <ul>
                        {pinnedComments.map((comment) =>
                            renderComment(comment),
                        )}
                    </ul>

                    <Localized id='comments-CommentsList--all-comments'>
                        <h2 className='title'>ALL COMMENTS</h2>
                    </Localized>
                </section>
            ) : null}
            <section className='all-comments'>
                <ul>{comments.map((comment) => renderComment(comment))}</ul>
                {!canComment ? null : (
                    <AddComment
                        parameters={parameters}
                        username={user.username}
                        imageURL={user.gravatarURLSmall}
                        translation={translationId}
                        users={users}
                        addComment={addComment}
                        contactPerson={contactPerson}
                        resetContactPerson={resetContactPerson}
                    />
                )}
            </section>
        </div>
    );
}

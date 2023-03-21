import { Localized } from '@fluent/react';
import React from 'react';
import { TranslationComment } from '~/api/comment';

import { AddComment } from '~/modules/comments/components/AddComment';
import { Comment } from '~/modules/comments/components/Comment';
import { useAddCommentAndRefresh } from '~/modules/comments/hooks';
import type { UserState } from '~/modules/user';
import type { TeamCommentState } from '~/modules/teamcomments';

import './TeamComments.css';

type Props = {
  contactPerson: string;
  initFocus: boolean;
  resetContactPerson: () => void;
  teamComments: TeamCommentState;
  togglePinnedStatus: (state: boolean, id: number) => void;
  user: UserState;
};

export function TeamComments({
  contactPerson,
  initFocus,
  teamComments: { comments, fetching },
  user,
  togglePinnedStatus,
  resetContactPerson,
}: Props): null | React.ReactElement<'section'> {
  const onAddComment = useAddCommentAndRefresh(null);

  if (fetching || !comments) {
    return null;
  }

  const canComment = user.isAuthenticated;
  if (!comments.length && !canComment) {
    return (
      <section className='team-comments'>
        <Localized id='entitydetails-Helpers--no-comments'>
          <p className='no-team-comments'>No comments available.</p>
        </Localized>
      </section>
    );
  }

  const renderComment = (comment: TranslationComment) => (
    <Comment
      comment={comment}
      canPin={user.isAdmin}
      key={comment.id}
      togglePinnedStatus={togglePinnedStatus}
    />
  );

  const pinnedComments = comments.filter((comment) => comment.pinned);
  const unpinnedComments = comments.filter((comment) => !comment.pinned);

  return (
    <section className='team-comments'>
      <div className='comments-list'>
        {pinnedComments.length ? (
          <section className='pinned-comments'>
            <Localized id='comments-CommentsList--pinned-comments'>
              <h2 className='title'>PINNED COMMENTS</h2>
            </Localized>
            <ul>{pinnedComments.map(renderComment)}</ul>
            {canComment || unpinnedComments.length > 0 ? (
              <Localized id='comments-CommentsList--all-comments'>
                <h2 className='title'>ALL COMMENTS</h2>
              </Localized>
            ) : null}
          </section>
        ) : null}
        <section className='all-comments'>
          <ul>{unpinnedComments.map(renderComment)}</ul>
          {canComment ? (
            <AddComment
              contactPerson={contactPerson}
              initFocus={initFocus}
              onAddComment={onAddComment}
              resetContactPerson={resetContactPerson}
              user={user}
            />
          ) : null}
        </section>
      </div>
    </section>
  );
}

import React from 'react';

import type { HistoryTranslation } from '~/api/translation';
import type { UserState } from '~/modules/user';
import {
  useAddCommentAndRefresh,
  useEditCommentAndRefresh,
  useDeleteCommentAndRefresh,
} from '../hooks';

import { AddComment } from './AddComment';
import { Comment } from './Comment';
import './CommentsList.css';

type Props = {
  translation: HistoryTranslation;
  user: UserState;
};

export function CommentsList({
  translation,
  user,
}: Props): React.ReactElement<'div'> {
  const onAddComment = useAddCommentAndRefresh(translation);
  const onDeleteComment = useDeleteCommentAndRefresh(translation);
  const onEditComment = useEditCommentAndRefresh(translation);

  return (
    <div className='comments-list'>
      <section className='all-comments'>
        <ul>
          {translation.comments.map((comment) => (
            <Comment
              comment={comment}
              key={comment.id}
              onDeleteComment={onDeleteComment}
              onEditComment={onEditComment}
              canEdit={user.username === comment.username}
              canDelete={user.username === comment.username || user.isPM}
              user={user}
            />
          ))}
        </ul>
        {user.isAuthenticated ? (
          <AddComment initFocus onAddComment={onAddComment} user={user} />
        ) : null}
      </section>
    </div>
  );
}

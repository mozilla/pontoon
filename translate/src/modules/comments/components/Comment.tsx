import { Localized } from '@fluent/react';
import parse from 'html-react-parser';
import React, { useState } from 'react';
// @ts-expect-error Working types are unavailable for react-linkify 0.2.2
import Linkify from 'react-linkify';
import ReactTimeAgo from 'react-time-ago';

import type { TranslationComment } from '~/api/comment';
import { UserAvatar, UserState } from '~/modules/user';

import './Comment.css';
import { AddComment } from './AddComment';

type Props = {
  comment: TranslationComment;
  canPin?: boolean;
  togglePinnedStatus?: (status: boolean, id: number) => void;
  onEditComment?: (id: number, content: string) => void;
  onDeleteComment?: (id: number) => void;
  canEdit?: boolean;
  canDelete?: boolean;
  user?: UserState;
};

export function Comment(props: Props): null | React.ReactElement<'li'> {
  const {
    comment,
    canPin,
    togglePinnedStatus,
    onEditComment,
    onDeleteComment,
    canEdit,
    canDelete,
    user,
  } = props;

  if (!comment) {
    return null;
  }

  const [isEditing, setIsEditing] = useState(false);

  const handlePinAndUnpin = () => {
    if (!togglePinnedStatus) {
      return;
    }
    togglePinnedStatus(!comment.pinned, comment.id);
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
  };

  const handleDelete = () => {
    if (!onDeleteComment) {
      return;
    }

    onDeleteComment(comment.id);
  };

  return (
    <li className={`comment${isEditing ? ' is-editing' : ''}`}>
      {!isEditing && (
        <UserAvatar
          username={comment.username}
          imageUrl={comment.userGravatarUrlSmall}
          userBanner={comment.userBanner}
        />
      )}
      <div className='container'>
        {isEditing && user ? (
          <AddComment
            initFocus
            initialContent={comment.content}
            onAddComment={(newContent) => {
              if (onEditComment) {
                onEditComment(comment.id, newContent);
                setIsEditing(false);
              }
            }}
            user={user}
          />
        ) : (
          <div className='content'>
            <div>
              <a
                className='comment-author'
                href={`/contributors/${comment.username}`}
                target='_blank'
                rel='noopener noreferrer'
                onClick={(e: React.MouseEvent) => e.stopPropagation()}
              >
                {comment.author}
              </a>
              <Linkify
                properties={{
                  target: '_blank',
                  rel: 'noopener noreferrer',
                }}
              >
                {/* We can safely use parse with comment.content as it is
                 * sanitized when coming from the DB. See:
                 *   - pontoon.base.forms.AddCommentForm(}
                 *   - pontoon.base.forms.HtmlField()
                 */}
                <span dir='auto'>{parse(comment.content)}</span>
              </Linkify>
              {!comment.pinned ? null : (
                <div className='comment-pin'>
                  <div className='fas fa-thumbtack'></div>
                  <Localized id='comments-Comment--pinned'>
                    <span className='pinned'>PINNED</span>
                  </Localized>
                </div>
              )}
            </div>
          </div>
        )}
        <div className='info'>
          <ReactTimeAgo
            dir='ltr'
            date={new Date(comment.dateIso)}
            title={`${comment.createdAt} UTC`}
          />
          {canPin ? (
            comment.pinned ? (
              // Unpin Button
              <Localized
                id='comments-Comment--unpin-button'
                attrs={{ title: true }}
              >
                <button
                  className='pin-button'
                  title='Unpin comment'
                  onClick={handlePinAndUnpin}
                >
                  {'UNPIN'}
                </button>
              </Localized>
            ) : (
              // Pin Button
              <Localized
                id='comments-Comment--pin-button'
                attrs={{ title: true }}
              >
                <button
                  className='pin-button'
                  title='Pin comment'
                  onClick={handlePinAndUnpin}
                >
                  {'PIN'}
                </button>
              </Localized>
            )
          ) : null}
          {canEdit && (
            <>
              {isEditing ? (
                <button className='pin-button' onClick={handleCancelEdit}>
                  {'CANCEL EDIT'}
                </button>
              ) : (
                <Localized id='comments-Comment--edit-button'>
                  <button
                    className='pin-button'
                    title='Edit comment'
                    onClick={handleEdit}
                  >
                    {'EDIT'}
                  </button>
                </Localized>
              )}
            </>
          )}
          {canDelete && (
            <Localized id='comments-Comment--delete-button'>
              <button
                className='pin-button'
                title='Delete comment'
                onClick={handleDelete}
              >
                {'DELETE'}
              </button>
            </Localized>
          )}
        </div>
      </div>
    </li>
  );
}

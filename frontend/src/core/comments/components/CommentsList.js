/* @flow */

import * as React from 'react';

import './CommentsList.css';

import { Comment, AddComment } from 'core/comments';

import type { NavigationParams } from 'core/navigation';
import type { TranslationComment, UsersType } from 'core/api';
import type { UserState } from 'core/user';
import type { HistoryTranslation } from 'modules/history'


type Props = {|
    comments: Array<TranslationComment>,
    parameters?: NavigationParams,
    translation?: HistoryTranslation,
    user: UserState,
    projectManager?: Object,
    users: Array<UsersType>,
    canComment: boolean,
    addComment: (string, ?number) => void,
    getUsers: () => void,
|};


export default function CommentsList(props: Props) {
    const {
        comments,
        parameters,
        translation,
        user,
        canComment,
        addComment,
        getUsers,
        users,
        projectManager,
    } = props;

    const translationId = translation ? translation.pk : null;

    return <div className='comments-list'>
        <ul>
            { comments.map(comment =>
                <Comment
                    comment={ comment }
                    key={ comment.id }
                />
            )}
        </ul>
        { !canComment ? null :
            <AddComment
                parameters={ parameters }
                user={ user.nameOrEmail }
                username={ user.username }
                imageURL={ user.gravatarURLSmall}
                translation={ translationId }
                projectManager={ projectManager }
                users={ users }
                addComment={ addComment }
                getUsers={ getUsers }
            />
        }
    </div>
}

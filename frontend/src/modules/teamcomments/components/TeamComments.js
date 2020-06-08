/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './TeamComments.css';

import { CommentsList } from 'core/comments';

import type { CommentState } from 'core/comments';
import type { NavigationParams } from 'core/navigation';
import type { UsersType } from 'core/api';
import type { UserState } from 'core/user';
import type { TeamCommentState } from 'modules/teamcomments';

type Props = {|
    parameters: NavigationParams,
    teamComments: TeamCommentState,
    user: UserState,
    projectManager: Object,
    users: CommentState,
    addComment: (string, ?number) => void,
    getUsers: () => void,
|};


export default function TeamComments(props: Props) {
    const { 
        teamComments, 
        user,
        parameters,
        projectManager,
        users,
        addComment,
        getUsers, 
    } = props;

    if (teamComments.fetching || !teamComments.comments) {
        return null;
    }

    const comments = teamComments.comments;

    let canComment = user.isAuthenticated;

    return <section className="team-comments">
        { !comments.length && !canComment ?
            <Localized id="entitydetails-Helpers--no-comments">
                <p className="no-team-comments">No comments available.</p>
            </Localized>
            :
            <CommentsList
                comments={ comments }
                parameters={ parameters }
                user={ user }
                projectManager={ projectManager }
                users={ users }
                canComment={ canComment }
                addComment={ addComment }
                getUsers={ getUsers }
            />
        }
    </section>
}

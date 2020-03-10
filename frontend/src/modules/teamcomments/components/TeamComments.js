/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './TeamComments.css';

import { CommentsList } from 'core/comments';

import type { UserState } from 'core/user';
import type { TeamCommentState } from 'modules/teamcomments';

type Props = {|
    teamComments: TeamCommentState,
    user: UserState,
    projectManager: Object,
    addComment: (string, ?number) => void,
    getUsers: () => void,
|};


export default function TeamComments(props: Props) {
    const { 
        teamComments, 
        user, 
        addComment, 
        getUsers, 
        projectManager
    } = props;

    let canComment = user.isAuthenticated;
    const comments = teamComments.comments;

    if (!comments) {
        return null;
    }

    return <section className="team-comments">
        { !comments.length && !canComment ?
            <Localized id="entitydetails-Helpers--no-comments">
                <p className="no-team-comments">No comments available.</p>
            </Localized>
            :
            <section className="team-comments">
                <CommentsList
                    comments={ comments }
                    user={ user }
                    canComment={ canComment }
                    addComment={ addComment }
                    getUsers={ getUsers }
                    projectManager={ projectManager }
                />
            </section>
        }
    </section>
}

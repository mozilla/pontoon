/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './TeamComments.css';

import { CommentsList } from 'core/comments';

import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';
import type { TeamCommentState } from 'modules/teamcomments';

type Props = {|
    parameters: NavigationParams,
    teamComments: TeamCommentState,
    user: UserState,
    users: UserState,
    projectManager: string,
    addComment: (string, ?number) => void,
    togglePinnedStatus: (boolean, number) => void,
    resetProjectManager: () => void,
|};

export default function TeamComments(props: Props) {
    const {
        teamComments,
        user,
        parameters,
        users,
        addComment,
        togglePinnedStatus,
        projectManager,
        resetProjectManager,
    } = props;

    if (teamComments.fetching || !teamComments.comments) {
        return null;
    }

    const comments = teamComments.comments;

    let canComment = user.isAuthenticated;
    const canPin = user.isAdmin;

    return (
        <section className='team-comments'>
            {!comments.length && !canComment ? (
                <Localized id='entitydetails-Helpers--no-comments'>
                    <p className='no-team-comments'>No comments available.</p>
                </Localized>
            ) : (
                <CommentsList
                    comments={comments}
                    parameters={parameters}
                    user={user}
                    users={users}
                    canComment={canComment}
                    canPin={canPin}
                    addComment={addComment}
                    togglePinnedStatus={togglePinnedStatus}
                    projectManager={projectManager}
                    resetProjectManager={resetProjectManager}
                />
            )}
        </section>
    );
}

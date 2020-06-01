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
    projectManager: Object,
    addComment: (string, ?number) => void,
|};


export default function TeamComments(props: Props) {
    const { teamComments, user, parameters, addComment } = props;

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
                canComment={ canComment }
                addComment={ addComment }
            />
        }
    </section>
}

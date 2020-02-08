/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';

import './TeamComment.css';

import { Comment } from 'core/comments';

import type { TeamCommentState } from 'core/comments';

type Props = {|
    teamComments: TeamCommentState,
|};


export default function TeamComment(props: Props) {
    const { teamComments } = props;

    if (!teamComments) {
        return <section className="team-comment">
            <Localized id="entitydetails-Helpers--no-comments">
                <p>No comments available.</p>
            </Localized>
        </section>
    }

    return <div>
        <ul>
            { teamComments.map(comment =>
                <Comment
                    comment={ comment }
                    key={ comment.id }
                />
            )}
        </ul>
    </div>

}

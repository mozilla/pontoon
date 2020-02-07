/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';
// import ReactTimeAgo from 'react-time-ago';

import './TeamComment.css';

// type Props = {|
// |};


export default function TeamComment(/*props: Props*/) {
    // const { comment } = props;

    return <section className="team-comment">
        <Localized id="entitydetails-Helpers--no-comments">
            <p>No comments available.</p>
        </Localized>
    </section>
}

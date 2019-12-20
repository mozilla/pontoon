/* @flow */

import * as React from 'react';

import type { TranslationComment } from 'core/api';

import { Comment, AddComment } from 'core/translation';


type Props = {|
    translationComments: Array<TranslationComment>,
|};


export default class Comments extends React.Component<Props> {
    render() {
        const { translationComments } = this.props;

        if (!translationComments) {
            return null;
        }

        return (
            <ul>
                <li>
                    { translationComments.map(content =>
                        <Comment comment={ content } />
                    )}
                </li>
                <li>
                    <AddComment />
                </li>
            </ul>
        )
    }
}

/* @flow */

import * as React from 'react';
import TimeAgo from 'react-timeago';

import './Translation.css';

import type { DBTranslation } from '../reducer';


type Props = {|
    translation: DBTranslation,
|};

/**
 * Render a translation in the History tab.
 *
 * Shows the translation's status, date, author and reviewer, as well as
 * the content of the translation.
 *
 * The status can be interact with if the user has sufficient permissions to
 * change said status.
 */
export default class Translation extends React.Component<Props> {
    getStatus() {
        const { translation } = this.props;

        if (translation.approved) {
            return 'approved';
        }
        if (translation.fuzzy) {
            return 'fuzzy';
        }
        if (translation.rejected) {
            return 'rejected';
        }
        return 'unreviewed';
    }

    getApprovalTitle() {
        const { translation } = this.props;

        if (translation.approved && translation.approved_user) {
            return `Approved by ${translation.approved_user}`;
        }
        if (translation.unapproved_user) {
            return `Unapproved by ${translation.unapproved_user}`;
        }
        return 'Not reviewed yet';
    }

    renderUser() {
        const { translation } = this.props;

        if (!translation.uid) {
            return <span>{ translation.user }</span>;
        }

        return <a
            href={ `/contributors/${translation.username}` }
            title={ this.getApprovalTitle() }
            target="_blank"
            rel="noopener noreferrer"
        >
            { translation.user }
        </a>
    }

    render() {
        const { translation } = this.props;

        return <li
            className={ 'translation ' + this.getStatus() }
        >
            <header>
                <div className="info">
                    { this.renderUser() }
                    <TimeAgo date={ translation.date_iso } title={ `${translation.date} UTC` } />
                </div>
                <menu className="toolbar">
                    <button
                        className={ (translation.approved ? 'unapprove' : 'approve') + ' fa' }
                        title={ translation.approved ? 'Unapprove' : 'Approve' }
                    ></button>
                    <button
                        className={ (translation.rejected ? 'unreject' : 'reject') + ' fa' }
                        title={ translation.rejected ? 'Unreject' : 'Reject' }
                    ></button>
                </menu>
            </header>
            <p>{ translation.string }</p>
        </li>;
    }
}

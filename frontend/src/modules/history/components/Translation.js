/* @flow */

import * as React from 'react';
import TimeAgo from 'react-timeago';
import { Localized } from 'fluent-react';

import './Translation.css';

import type { Locale } from 'core/locales';
import type { UserState } from 'core/user';
import type { DBTranslation } from '../reducer';


type Props = {|
    canReview: boolean,
    translation: DBTranslation,
    locale: Locale,
    user: UserState,
    deleteTranslation: (number) => void,
    updateEditorTranslation: (string) => void,
    updateTranslationStatus: (number, string) => void,
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
    approve = () => {
        this.props.updateTranslationStatus(this.props.translation.pk, 'approve');
    }

    unapprove = () => {
        this.props.updateTranslationStatus(this.props.translation.pk, 'unapprove');
    }

    reject = () => {
        this.props.updateTranslationStatus(this.props.translation.pk, 'reject');
    }

    unreject = () => {
        this.props.updateTranslationStatus(this.props.translation.pk, 'unreject');
    }

    delete = () => {
        this.props.deleteTranslation(this.props.translation.pk);
    }

    copyTranslationIntoEditor = () => {
        this.props.updateEditorTranslation(this.props.translation.string);
    }

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
            target='_blank'
            rel='noopener noreferrer'
        >
            { translation.user }
        </a>
    }

    render() {
        const { canReview, translation, locale, user } = this.props;

        // Does the currently logged in user own this translation?
        const ownTranslation = (
            user && user.username &&
            user.username === translation.username
        );

        let className = 'translation ' + this.getStatus();
        if (canReview) {
            // This user is a translator for the current locale, they can
            // perform all review actions.
            className += ' can-approve can-reject';
        }
        else if (ownTranslation && !translation.approved) {
            // This user owns the translation and it's not approved, they
            // can only reject or unreject it.
            className += ' can-reject';
        }

        let canDelete = canReview || ownTranslation;

        return <Localized id='history-translation-copy' attrs={{ title: true }}>
            <li
                className={ className }
                title='Copy Into Translation (Tab)'
                onClick={ this.copyTranslationIntoEditor }
            >
                <header className='clearfix'>
                    <div className='info'>
                        { this.renderUser() }
                        <TimeAgo
                            dir='ltr'
                            date={ translation.date_iso }
                            title={ `${translation.date} UTC` }
                        />
                    </div>
                    <menu className='toolbar'>
                    { (!translation.rejected || !canDelete ) ? null :
                        // Delete Button
                        <Localized
                            id='history-translation-button-delete'
                            attrs={{ title: true }}
                        >
                            <button
                                className='delete far'
                                title='Delete'
                                onClick={ this.delete }
                            />
                        </Localized>
                    }
                    { translation.approved ?
                        // Unapprove Button
                        <Localized
                            id='history-translation-button-unapprove'
                            attrs={{ title: true }}
                        >
                            <button
                                className='unapprove fa'
                                title='Unapprove'
                                onClick={ this.unapprove }
                            />
                        </Localized>
                        :
                        // Approve Button
                        <Localized
                            id='history-translation-button-approve'
                            attrs={{ title: true }}
                        >
                            <button
                                className='approve fa'
                                title='Approve'
                                onClick={ this.approve }
                            />
                        </Localized>
                    }
                    { translation.rejected ?
                        // Unreject Button
                        <Localized
                            id='history-translation-button-unreject'
                            attrs={{ title: true }}
                        >
                            <button
                                className='unreject fa'
                                title='Unreject'
                                onClick={ this.unreject }
                            />
                        </Localized>
                        :
                        // Reject Button
                        <Localized
                            id='history-translation-button-reject'
                            attrs={{ title: true }}
                        >
                            <button
                                className='reject fa'
                                title='Reject'
                                onClick={ this.reject }
                            />
                        </Localized>
                    }
                    </menu>
                </header>
                <p
                    dir={ locale.direction }
                    lang={ locale.code }
                    data-script={ locale.script }
                >
                    { translation.string }
                </p>
            </li>
        </Localized>;
    }
}

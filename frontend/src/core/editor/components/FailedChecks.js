/* @flow */

import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Localized } from '@fluent/react';

import './FailedChecks.css';

import * as user from 'core/user';

import { actions, useUpdateTranslationStatus } from '..';

import type { UserState } from 'core/user';

type FailedChecksProps = {|
    sendTranslation: (ignoreWarnings?: boolean) => void,
|};

/**
 * Shows a list of failed checks (errors and warnings) and a button to ignore
 * those checks and proceed anyway.
 */
export default function FailedChecks(props: FailedChecksProps) {
    const dispatch = useDispatch();

    const errors = useSelector((state) => state.editor.errors);
    const warnings = useSelector((state) => state.editor.warnings);
    const source = useSelector((state) => state.editor.source);
    const userState = useSelector((state) => state.user);
    const isTranslator = useSelector(user.selectors.isTranslator);

    const updateTranslationStatus = useUpdateTranslationStatus();

    if (!errors.length && !warnings.length) {
        return null;
    }

    function resetChecks() {
        dispatch(actions.resetFailedChecks());
    }

    function approveAnyway() {
        if (typeof source === 'number') {
            updateTranslationStatus(source, 'approve', true);
        }
    }

    function submitAnyway() {
        props.sendTranslation(true);
    }

    return (
        <div className='failed-checks'>
            <Localized
                id='editor-FailedChecks--close'
                attrs={{ ariaLabel: true }}
            >
                <button
                    aria-label='Close failed checks popup'
                    className='close'
                    onClick={resetChecks}
                >
                    ×
                </button>
            </Localized>
            <Localized id='editor-FailedChecks--title'>
                <p className='title'>The following checks have failed</p>
            </Localized>
            <ul>
                {errors.map((error, key) => (
                    <li className='error' key={key}>
                        {error}
                    </li>
                ))}
                {warnings.map((warning, key) => (
                    <li className='warning' key={key}>
                        {warning}
                    </li>
                ))}
            </ul>
            <MainAction
                source={source}
                user={userState}
                isTranslator={isTranslator}
                errors={errors}
                approveAnyway={approveAnyway}
                submitAnyway={submitAnyway}
            />
        </div>
    );
}

type MainActionProps = {|
    source: number,
    user: UserState,
    isTranslator: boolean,
    errors: Array<string>,
    approveAnyway: () => void,
    submitAnyway: () => void,
|};

/**
 * Shows a button to ignore failed checks and proceed with the main editor action.
 */
function MainAction(props: MainActionProps) {
    const {
        source,
        user,
        isTranslator,
        errors,
        approveAnyway,
        submitAnyway,
    } = props;

    if (source === 'stored' || errors.length) {
        return null;
    }

    if (source !== 'submitted') {
        return (
            <Localized id='editor-FailedChecks--approve-anyway'>
                <button className='approve anyway' onClick={approveAnyway}>
                    Approve anyway
                </button>
            </Localized>
        );
    }

    if (user.settings.forceSuggestions || !isTranslator) {
        return (
            <Localized id='editor-FailedChecks--suggest-anyway'>
                <button className='suggest anyway' onClick={submitAnyway}>
                    Suggest anyway
                </button>
            </Localized>
        );
    }

    return (
        <Localized id='editor-FailedChecks--save-anyway'>
            <button className='save anyway' onClick={submitAnyway}>
                Save anyway
            </button>
        </Localized>
    );
}

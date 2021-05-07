/* @flow */

import * as React from 'react';
import { Localized } from '@fluent/react';
import { Link } from 'react-router-dom';

import './ResourceProgress.css';

import ProgressChart from './ProgressChart';

import { asLocaleString, useOnDiscard } from 'core/utils';

import type { NavigationParams } from 'core/navigation';
import type { Stats } from 'core/stats';

type Props = {|
    parameters: NavigationParams,
    stats: Stats,
|};

type State = {|
    visible: boolean,
|};

type ResourceProgressProps = {
    currentPath: string,
    percent: number,
    stats: Stats,
    onDiscard: (e: MouseEvent) => void,
};

function ResourceProgress({
    currentPath,
    percent,
    stats,
    onDiscard,
}: ResourceProgressProps) {
    const {
        approved,
        fuzzy,
        warnings,
        errors,
        missing,
        unreviewed,
        total,
    } = stats;

    const ref = React.useRef(null);
    useOnDiscard(ref, onDiscard);

    return (
        <aside ref={ref} className='menu'>
            <div className='main'>
                <header>
                    <h2>
                        <Localized id='resourceprogress-ResourceProgress--all-strings'>
                            ALL STRINGS
                        </Localized>
                        <span className='value'>{asLocaleString(total)}</span>
                    </h2>
                    <h2 className='small'>
                        <Localized id='resourceprogress-ResourceProgress--unreviewed'>
                            UNREVIEWED
                        </Localized>
                        <span className='value'>
                            {asLocaleString(unreviewed)}
                        </span>
                    </h2>
                </header>
                <ProgressChart stats={stats} size={220} />
                <span className='percent'>{percent}</span>
            </div>
            <div className='details'>
                <div className='approved'>
                    <span className='title'>
                        <Localized id='resourceprogress-ResourceProgress--translated'>
                            TRANSLATED
                        </Localized>
                    </span>
                    <p className='value' onClick={onDiscard}>
                        <Link
                            to={{
                                pathname: currentPath,
                                search: '?status=translated',
                            }}
                        >
                            {asLocaleString(approved)}
                        </Link>
                    </p>
                </div>
                <div className='fuzzy'>
                    <span className='title'>
                        <Localized id='resourceprogress-ResourceProgress--fuzzy'>
                            FUZZY
                        </Localized>
                    </span>
                    <p className='value' onClick={onDiscard}>
                        <Link
                            to={{
                                pathname: currentPath,
                                search: '?status=fuzzy',
                            }}
                        >
                            {asLocaleString(fuzzy)}
                        </Link>
                    </p>
                </div>
                <div className='warnings'>
                    <span className='title'>
                        <Localized id='resourceprogress-ResourceProgress--warnings'>
                            WARNINGS
                        </Localized>
                    </span>
                    <p className='value' onClick={onDiscard}>
                        <Link
                            to={{
                                pathname: currentPath,
                                search: '?status=warnings',
                            }}
                        >
                            {asLocaleString(warnings)}
                        </Link>
                    </p>
                </div>
                <div className='errors'>
                    <span className='title'>
                        <Localized id='resourceprogress-ResourceProgress--errors'>
                            ERRORS
                        </Localized>
                    </span>
                    <p className='value' onClick={onDiscard}>
                        <Link
                            to={{
                                pathname: currentPath,
                                search: '?status=errors',
                            }}
                        >
                            {asLocaleString(errors)}
                        </Link>
                    </p>
                </div>
                <div className='missing'>
                    <span className='title'>
                        <Localized id='resourceprogress-ResourceProgress--missing'>
                            MISSING
                        </Localized>
                    </span>
                    <p className='value' onClick={onDiscard}>
                        <Link
                            to={{
                                pathname: currentPath,
                                search: '?status=missing',
                            }}
                        >
                            {asLocaleString(missing)}
                        </Link>
                    </p>
                </div>
            </div>
        </aside>
    );
}

/**
 * Show a panel with progress chart and stats for the current resource.
 */
export default class ResourceProgressBase extends React.Component<
    Props,
    State,
> {
    constructor(props: Props) {
        super(props);
        this.state = {
            visible: false,
        };
    }

    toggleVisibility: () => void = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    };

    handleDiscard: () => void = () => {
        this.setState({
            visible: false,
        });
    };

    render(): null | React.Element<'div'> {
        const { parameters, stats } = this.props;

        // Do not show resource progress until stats are available
        if (!stats.total) {
            return null;
        }

        const complete = stats.approved + stats.warnings;
        const percent = Math.floor((complete / stats.total) * 100);
        const currentPath = `/${parameters.locale}/${parameters.project}/${parameters.resource}/`;

        return (
            <div className='progress-chart'>
                <div className='selector' onClick={this.toggleVisibility}>
                    <ProgressChart stats={stats} size={44} />
                    <span className='percent unselectable'>{percent}</span>
                </div>
                {this.state.visible && (
                    <ResourceProgress
                        currentPath={currentPath}
                        percent={percent}
                        stats={stats}
                        onDiscard={this.handleDiscard}
                    />
                )}
            </div>
        );
    }
}

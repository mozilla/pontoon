/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';
import { Localized } from '@fluent/react';

import './UserMenu.css';
import FileUpload from './FileUpload';
import SignOut from './SignOut';

import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';


type Props = {
    isReadOnly: boolean,
    isTranslator: boolean,
    parameters: NavigationParams,
    signOut: () => void,
    user: UserState,
};

type State = {|
    visible: boolean,
|};


/**
 * Renders user menu.
 */
export class UserMenuBase extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            visible: false,
        };
    }

    toggleVisibility = () => {
        this.setState((state) => {
            return { visible: !state.visible };
        });
    }

    // This method is called by the Higher-Order Component `onClickOutside`
    // when a user clicks outside the user menu.
    handleClickOutside = () => {
        this.setState({
            visible: false,
        });
    }

    render() {
        const { isReadOnly, isTranslator, parameters, signOut, user } = this.props;

        const locale = parameters.locale;
        const project = parameters.project;
        const resource = parameters.resource;

        const tmHref = `/${locale}/${project}/${locale}.${project}.tmx`;
        const transHref = `/download/?code=${locale}&slug=${project}&part=${resource}`;

        const canDownload = (
            project !== 'all-projects' &&
            resource !== 'all-resources'
        );

        const canUpload = (
            /* TODO: Also disable for subpages (in-context l10n) when supported */
            canDownload &&
            isTranslator &&
            !isReadOnly
        );

        return <div className="user-menu">
            <div
                className="selector"
                onClick={ this.toggleVisibility }
            >
                { user.isAuthenticated ?
                <img src={ user.gravatarURLSmall } alt="User avatar" /> :
                <div className="menu-icon fa fa-bars" />
                }
            </div>

            { !this.state.visible ? null :
            <ul className="menu">
                { !user.isAuthenticated ? null :
                <React.Fragment>
                    <li className="details">
                        <a href={ `/contributors/${user.username}/` }>
                            <img src={ user.gravatarURLBig } alt="User avatar" />
                            <p className="name">{ user.nameOrEmail }</p>
                            <p className="email">{ user.email }</p>
                        </a>
                    </li>
                    <li className="horizontal-separator"></li>
                </React.Fragment>
                }

                <li>
                    <Localized
                        id="user-UserMenu--download-tm"
                        glyph={
                            <i className="fa fa-cloud-download-alt fa-fw"></i>
                        }
                    >
                        <a href={ tmHref }>
                            { '<glyph></glyph>Download Translation Memory' }
                        </a>
                    </Localized>
                </li>

                { !canDownload ? null :
                <li>
                    <Localized
                        id="user-UserMenu--download-translations"
                        glyph={
                            <i className="fa fa-cloud-download-alt fa-fw"></i>
                        }
                    >
                        <a href={ transHref }>
                            { '<glyph></glyph>Download Translations' }
                        </a>
                    </Localized>
                </li>
                }

                { !canUpload ? null :
                <li>
                    <FileUpload parameters={ parameters } />
                </li>
                }

                <li className="horizontal-separator"></li>

                <li>
                    <Localized
                        id="user-UserMenu--terms"
                        glyph={
                            <i className="fa fa-gavel fa-fw"></i>
                        }
                    >
                        <a
                            href="/terms/"
                            rel="noopener noreferrer"
                            target="_blank"
                        >
                            { '<glyph></glyph>Terms of Use' }
                        </a>
                    </Localized>
                </li>

                <li>
                    <Localized
                        id="user-UserMenu--github"
                        glyph={
                            <i className="fab fa-github fa-fw"></i>
                        }
                    >
                        <a
                            href="https://github.com/mozilla/pontoon/"
                            rel="noopener noreferrer"
                            target="_blank"
                        >
                            { '<glyph></glyph>Hack it on GitHub' }
                        </a>
                    </Localized>
                </li>

                <li>
                    <Localized
                        id="user-UserMenu--feedback"
                        glyph={
                            <i className="fa fa-comment-dots fa-fw"></i>
                        }
                    >
                        <a
                            href="https://discourse.mozilla.org/c/pontoon"
                            rel="noopener noreferrer"
                            target="_blank"
                        >
                            { '<glyph></glyph>Give Feedback' }
                        </a>
                    </Localized>
                </li>

                <li>
                    <Localized
                        id="user-UserMenu--help"
                        glyph={
                            <i className="fa fa-life-ring fa-fw"></i>
                        }
                    >
                        <a
                            href="https://mozilla-l10n.github.io/localizer-documentation/tools/pontoon/"
                            rel="noopener noreferrer"
                            target="_blank"
                        >
                            { '<glyph></glyph>Help' }
                        </a>
                    </Localized>
                </li>

                { !user.isAuthenticated ? null :
                <li className="horizontal-separator"></li>
                }

                { !user.isAdmin ? null :
                <React.Fragment>
                    <li>
                        <Localized
                            id="user-UserMenu--admin"
                            glyph={
                                <i className="fa fa-wrench fa-fw"></i>
                            }
                        >
                            <a href="/admin/">
                                { '<glyph></glyph>Admin' }
                            </a>
                        </Localized>
                    </li>
                    <li>
                        <Localized
                            id="user-UserMenu--admin-project"
                            glyph={
                                <i className="fa fa-wrench fa-fw"></i>
                            }
                        >
                            <a href={ `/admin/projects/${project}/` }>
                                { '<glyph></glyph>Admin · Current Project' }
                            </a>
                        </Localized>
                    </li>
                </React.Fragment>
                }

                { !user.isAuthenticated ? null :
                <React.Fragment>
                    <li>
                        <Localized
                            id="user-UserMenu--settings"
                            glyph={
                                <i className="fa fa-cog fa-fw"></i>
                            }
                        >
                            <a href="/settings/">
                                { '<glyph></glyph>Settings' }
                            </a>
                        </Localized>
                    </li>
                    <li>
                        <SignOut signOut={ signOut } />
                    </li>
                </React.Fragment>
                }
            </ul>
            }
        </div>;
    }
}

export default onClickOutside(UserMenuBase);

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
                    <img
                        src={ user.gravatarURLSmall }
                        alt=""
                        height="44"
                        width="44"
                    />
                    :
                    <div className="menu-icon fa fa-bars" />
                }
            </div>

            { !this.state.visible ? null :
            <ul className="menu">
                { !user.isAuthenticated ? null :
                <React.Fragment>
                    <li className="details">
                        <a href={ `/contributors/${user.username}/` }>
                            <img
                                src={ user.gravatarURLBig }
                                alt=""
                                height="88"
                                width="88"
                            />
                            <p className="name">{ user.nameOrEmail }</p>
                            <p className="email">{ user.email }</p>
                        </a>
                    </li>
                    <li className="horizontal-separator"></li>
                </React.Fragment>
                }

                <li>
                    <Localized
                        id="user-UserMenu--download-terminology"
                        elems={{ glyph: <i className="fa fa-cloud-download-alt fa-fw" /> }}
                    >
                        <a href={ `/terminology/${locale}.tbx` }>
                            { '<glyph></glyph>Download Terminology' }
                        </a>
                    </Localized>
                </li>

                <li>
                    <Localized
                        id="user-UserMenu--download-tm"
                        elems={{ glyph: <i className="fa fa-cloud-download-alt fa-fw" /> }}
                    >
                        <a href={ `/${locale}/${project}/${locale}.${project}.tmx` }>
                            { '<glyph></glyph>Download Translation Memory' }
                        </a>
                    </Localized>
                </li>

                { !canDownload ? null :
                <li>
                    <Localized
                        id="user-UserMenu--download-translations"
                        elems={{ glyph: <i className="fa fa-cloud-download-alt fa-fw" /> }}
                    >
                        <a href={ `/download/?code=${locale}&slug=${project}&part=${resource}` }>
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
                        elems={{ glyph: <i className="fa fa-gavel fa-fw" /> }}
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
                        elems={{ glyph: <i className="fab fa-github fa-fw" /> }}
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
                        elems={{ glyph: <i className="fa fa-comment-dots fa-fw" /> }}
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
                        elems={{ glyph: <i className="fa fa-life-ring fa-fw" /> }}
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
                            elems={{ glyph: <i className="fa fa-wrench fa-fw" /> }}
                        >
                            <a href="/admin/">
                                { '<glyph></glyph>Admin' }
                            </a>
                        </Localized>
                    </li>
                    <li>
                        <Localized
                            id="user-UserMenu--admin-project"
                            elems={{ glyph: <i className="fa fa-wrench fa-fw" /> }}
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
                            elems={{ glyph: <i className="fa fa-cog fa-fw" /> }}
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

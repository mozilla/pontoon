/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';
import { Localized } from 'fluent-react';

import './UserMenu.css';

import SignOut from './SignOut';

import type { NavigationParams } from 'core/navigation';
import type { UserState } from 'core/user';


type Props = {
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
        const { parameters, signOut, user } = this.props;

        return <div className="user-menu">
            <div
                className="button selector"
                onClick={ this.toggleVisibility }
            >
                { user.isAuthenticated ?
                <img src={ user.gravatarURLSmall } alt="" /> :
                <div className="menu-icon fa fa-bars" />
                }
            </div>

            { !this.state.visible ? null :
            <div className="menu"><ul>
                { !user.isAuthenticated ? null :
                <li className="details">
                    <a href="/profile/">
                        <img src={ user.gravatarURLBig } alt="User avatar" />
                        <p className="name">{ user.nameOrEmail }</p>
                        <p className="email">{ user.email }</p>
                    </a>
                </li>
                }

                { !user.isAuthenticated ? null :
                <li className="horizontal-separator"></li>
                }

                <li>
                    <Localized
                        id="user-UserMenu--download-tm"
                        glyph={
                            <i className="fa fa-cloud-download-alt fa-fw"></i>
                        }
                    >
                        <a href={ `/${parameters.locale}/${parameters.project}/${parameters.locale}.${parameters.project}.tmx` }>
                            { '<glyph></glyph>Download Translation Memory' }
                        </a>
                    </Localized>
                </li>

                <li className="horizontal-separator"></li>

                <li>
                    <Localized
                        id="user-UserMenu--top-contributors"
                        glyph={
                            <i className="fa fa-trophy fa-fw"></i>
                        }
                    >
                        <a href="/contributors/">
                            { '<glyph></glyph>Top Contributors' }
                        </a>
                    </Localized>
                </li>

                <li>
                    <Localized
                        id="user-UserMenu--machinery"
                        glyph={
                            <i className="fa fa-search fa-fw"></i>
                        }
                    >
                        <a href="/machinery/">
                            { '<glyph></glyph>Machinery' }
                        </a>
                    </Localized>
                </li>

                <li>
                    <Localized
                        id="user-UserMenu--terms"
                        glyph={
                            <i className="fa fa-gavel fa-fw"></i>
                        }
                    >
                        <a href="/terms/">
                            { '<glyph></glyph>Terms of Use' }
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
                        <a href="https://mozilla-l10n.github.io/localizer-documentation/tools/pontoon/">
                            { '<glyph></glyph>Help' }
                        </a>
                    </Localized>
                </li>

                { !user.isAuthenticated ? null :
                <li className="horizontal-separator"></li>
                }

                { !user.isAdmin ? null :
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
                }

                { !user.isAdmin ? null :
                <li>
                    <Localized
                        id="user-UserMenu--admin-project"
                        glyph={
                            <i className="fa fa-wrench fa-fw"></i>
                        }
                    >
                        <a href={ `/admin/projects/${parameters.project}/` }>
                            { '<glyph></glyph>Admin · Current Project' }
                        </a>
                    </Localized>
                </li>
                }

                { !user.isAuthenticated ? null :
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
                }

                { !user.isAuthenticated ? null :
                <li>
                    <SignOut signOut={ signOut } />
                </li>
                }
            </ul></div>
            }
        </div>;
    }
}

export default onClickOutside(UserMenuBase);

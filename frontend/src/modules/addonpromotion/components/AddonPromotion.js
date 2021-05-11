/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import { Localized } from '@fluent/react';

import './AddonPromotion.css';

import * as user from 'core/user';

import type { UserState } from 'core/user';

type Props = {|
    user: UserState,
|};

type InternalProps = {
    ...Props,
    dispatch: Function,
};

type State = {|
    installed: boolean,
|};

/**
 * Renders Pontoon Add-On promotion banner.
 */
export class AddonPromotionBase extends React.Component<InternalProps, State> {
    constructor(props: InternalProps) {
        super(props);
        this.state = {
            installed: false,
        };
    }

    componentDidMount() {
        window.addEventListener('message', this.handleMessages);
    }

    componentWillUnmount() {
        window.removeEventListener('message', this.handleMessages);
    }

    handleMessages: (event: MessageEvent) => void = (event: MessageEvent) => {
        const data = JSON.parse(((event.data: any): string));
        if (data._type === 'PontoonAddonInfo') {
            if (data.value.installed) {
                this.setState({
                    installed: true,
                });
            }
        }
    };

    handleDismiss: () => void = () => {
        this.props.dispatch(user.actions.dismissAddonPromotion());
    };

    render(): null | React.Element<'div'> {
        const { user } = this.props;

        // User not authenticated or promotion dismissed
        if (!user.isAuthenticated || user.hasDismissedAddonPromotion) {
            return null;
        }

        // Add-On installed
        if (
            this.state.installed ||
            (window.PontoonAddon && window.PontoonAddon.installed)
        ) {
            return null;
        }

        const isFirefox = navigator.userAgent.indexOf('Firefox') !== -1;
        const isChrome = navigator.userAgent.indexOf('Chrome') !== -1;

        let downloadHref = '';

        if (isFirefox) {
            downloadHref =
                'https://addons.mozilla.org/firefox/addon/pontoon-tools/';
        }

        if (isChrome) {
            downloadHref =
                'https://chrome.google.com/webstore/detail/pontoon-add-on/gnbfbnpjncpghhjmmhklfhcglbopagbb';
        }

        // Page not loaded in Firefox or Chrome (add-on not available for other browsers)
        if (!downloadHref) {
            return null;
        }

        return (
            <div className='addon-promotion'>
                <div className='container'>
                    <Localized
                        id='addonpromotion-AddonPromotion--dismiss'
                        attrs={{ ariaLabel: true }}
                    >
                        <button
                            className='dismiss'
                            aria-label='Dismiss'
                            onClick={this.handleDismiss}
                        >
                            ×
                        </button>
                    </Localized>

                    <Localized id='addonpromotion-AddonPromotion--text'>
                        <p className='text'>
                            Take your Pontoon notifications everywhere with the
                            official Pontoon Add-on.
                        </p>
                    </Localized>

                    <Localized id='addonpromotion-AddonPromotion--get'>
                        <a className='get' href={downloadHref}>
                            Get Pontoon Add-On
                        </a>
                    </Localized>
                </div>
            </div>
        );
    }
}

const mapStateToProps = (state: Object): Props => {
    return {
        user: state[user.NAME],
    };
};

export default (connect(mapStateToProps)(AddonPromotionBase): any);

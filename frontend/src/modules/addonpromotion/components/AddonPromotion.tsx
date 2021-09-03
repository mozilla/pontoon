import * as React from 'react';
import { connect } from 'react-redux';
import { Localized } from '@fluent/react';

import './AddonPromotion.css';

import * as user from 'core/user';

import type { UserState } from 'core/user';
import { RootState } from 'store';

type Props = {
    user: UserState;
};

type InternalProps = Props & {
    dispatch: (...args: Array<any>) => any;
};

type State = {
    installed: boolean;
};

interface PontoonAddonInfo {
    installed?: boolean;
}

interface PontoonAddonInfoMessage {
    _type?: 'PontoonAddonInfo';
    value?: PontoonAddonInfo;
}

interface WindowWithInfo extends Window {
    PontoonAddon?: PontoonAddonInfo;
}

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

    // Hide Add-On Promotion if Add-On installed while active
    handleMessages: (event: MessageEvent) => void = (event: MessageEvent) => {
        // only allow messages from authorized senders (extension content script, or Pontoon itself)
        if (event.origin !== window.origin || event.source !== window) {
            return;
        }
        let data: PontoonAddonInfoMessage;
        switch (typeof event.data) {
            case 'object':
                data = event.data;
                break;
            case 'string':
                // backward compatibility
                // TODO: remove some reasonable time after https://github.com/MikkCZ/pontoon-addon/pull/155 is released
                // and convert this switch into a condition
                try {
                    data = JSON.parse(event.data);
                } catch (_) {
                    return;
                }
                break;
            default:
                return;
        }
        if (
            data?._type === 'PontoonAddonInfo' &&
            data?.value?.installed === true
        ) {
            this.setState({ installed: true });
        }
    };

    handleDismiss: () => void = () => {
        this.props.dispatch(user.actions.dismissAddonPromotion());
    };

    render(): null | React.ReactElement<'div'> {
        const { user } = this.props;

        // User not authenticated or promotion dismissed
        if (!user.isAuthenticated || user.hasDismissedAddonPromotion) {
            return null;
        }

        // Add-On installed
        if (
            this.state.installed ||
            (window as WindowWithInfo).PontoonAddon?.installed === true
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

const mapStateToProps = (state: RootState): Props => {
    return {
        user: state[user.NAME],
    };
};

export default connect(mapStateToProps)(AddonPromotionBase) as any;

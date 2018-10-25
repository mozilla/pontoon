/* @flow */

import * as React from 'react';
import { connect } from 'react-redux';
import { LocalizationProvider } from 'fluent-react/compat';

import * as l10n from 'core/l10n';


type Props = {|
    l10n: l10n.L10nState,
|};

type InternalProps = {|
    ...Props,
    children: React.Node,
    dispatch: Function,
|};


/**
 * Localization provider for this application.
 *
 * This Component is in charge of fetching translations for the application's
 * context and providing them to the underlying Localized elements.
 *
 * Until the translations are received, a loader is displayed.
 */
export class AppLocalizationProviderBase extends React.Component<InternalProps> {
    componentDidMount() {
        // $FLOW_IGNORE: we count on the 'lang' attribute being set.
        const locale = document.documentElement.lang;
        this.props.dispatch(l10n.actions.get(locale));
    }

    render() {
        const { children, l10n } = this.props;

        if (!l10n.bundles.length) {
            // Show a loader.
            return <div>LOADING</div>;
        }

        return <LocalizationProvider bundles={ l10n.bundles }>
            { children }
        </LocalizationProvider>;
    }
}


const mapStateToProps = (state: Object): Props => {
    return {
        l10n: state[l10n.NAME],
    };
};

export default connect(mapStateToProps)(AppLocalizationProviderBase);

import * as React from 'react';
import { connect } from 'react-redux';
import { LocalizationProvider } from '@fluent/react';
import 'intl-pluralrules';

import * as l10n from 'core/l10n';
import { RootState } from 'store';

type Props = {
    l10n: l10n.L10nState;
};

type InternalProps = Props & {
    children: React.ReactNode;
    dispatch: (...args: Array<any>) => any;
};

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
        // By default, we want to use the user's browser preferences to choose
        // which locales to fetch and show.
        let locales = navigator.languages;

        // However, if the user has chosen a specific locale, we want to
        // fetch and show that instead.
        // We use the `<html lang="">` attribute in the index.html file
        // to pass the user defined locale if there is one.
        if (document.documentElement && document.documentElement.lang) {
            locales = [document.documentElement.lang];
        }

        this.props.dispatch(l10n.actions.get(locales));
    }

    render(): React.ReactElement<React.ElementType> {
        const { children, l10n } = this.props;

        return (
            <LocalizationProvider l10n={l10n.localization}>
                {children}
            </LocalizationProvider>
        );
    }
}

const mapStateToProps = (state: RootState): Props => {
    return {
        l10n: state[l10n.NAME],
    };
};

export default connect(mapStateToProps)(AppLocalizationProviderBase) as any;

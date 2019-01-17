/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';

import './EditorSettings.css';

import type { Settings } from 'core/user';


type Props = {|
    settings: Settings,
    updateSettings: Function,
|};

type State = {|
    visible: boolean,
|};


/*
 * Renders settings to be used to customize interactions with the Editor.
 */
export class EditorSettingsBase extends React.Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            visible: false,
        };
    }

    toggleVisibility = () => {
        this.setState({
            visible: !this.state.visible,
        });
    }

    // This method is called by the Higher-Order Component `onClickOutside`
    // when a user clicks outside the search panel.
    handleClickOutside = () => {
        this.setState({
            visible: false,
        });
    }

    toggleSetting(setting: string) {
        return () => {
            const { settings } = this.props;
            const newSettings = {};
            newSettings[setting] = !settings[setting];
            this.props.updateSettings(newSettings);
        };
    }

    render() {
        const { settings } = this.props;

        return <div className="editor-settings">
            <div
                className="selector fa fa-cog"
                title="Settings"
                onClick={ this.toggleVisibility }
            />
            { !this.state.visible ? null :
            <ul className="menu">
                <li
                    className={ 'check-box' + (settings.runQualityChecks ? ' enabled' : '') }
                    title="Run Translate Toolkit checks before submitting translations"
                    onClick={ this.toggleSetting('runQualityChecks') }
                >
                    <i className="fa fa-fw"></i>
                    Translate Toolkit Checks
                </li>
                <li
                    className={ 'check-box' + (settings.forceSuggestions ? ' enabled' : '') }
                    title="Save suggestions instead of translations"
                    onClick={ this.toggleSetting('forceSuggestions') }
                >
                    <i className="fa fa-fw"></i>
                    Make Suggestions
                </li>
                <li className="horizontal-separator"></li>
                <li>
                    <a href="/settings/">Change All Settings</a>
                </li>
            </ul>
            }
        </div>;
    }
}

export default onClickOutside(EditorSettingsBase);

/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';
import { Localized } from '@fluent/react';

import './EditorSettings.css';

import type { Settings } from 'core/user';

type Props = {|
    settings: Settings,
    updateSetting: Function,
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
        this.setState((state) => {
            return { visible: !state.visible };
        });
    };

    // This method is called by the Higher-Order Component `onClickOutside`
    // when a user clicks outside the search panel.
    handleClickOutside = () => {
        this.setState({
            visible: false,
        });
    };

    toggleSetting(setting: string) {
        return () => {
            this.props.updateSetting(setting, !this.props.settings[setting]);
            this.toggleVisibility();
        };
    }

    render() {
        const { settings } = this.props;

        return (
            <div className='editor-settings'>
                <div
                    className='selector fa fa-cog'
                    title='Settings'
                    onClick={this.toggleVisibility}
                />

                {!this.state.visible ? null : (
                    <ul className='menu'>
                        <Localized
                            id='editor-EditorSettings--toolkit-checks'
                            attrs={{ title: true }}
                            elems={{ glyph: <i className='fa fa-fw' /> }}
                        >
                            <li
                                className={
                                    'check-box' +
                                    (settings.runQualityChecks
                                        ? ' enabled'
                                        : '')
                                }
                                title='Run Translate Toolkit checks before submitting translations'
                                onClick={this.toggleSetting('runQualityChecks')}
                            >
                                {'<glyph></glyph>Translate Toolkit Checks'}
                            </li>
                        </Localized>

                        <Localized
                            id='editor-EditorSettings--force-suggestions'
                            attrs={{ title: true }}
                            elems={{ glyph: <i className='fa fa-fw' /> }}
                        >
                            <li
                                className={
                                    'check-box' +
                                    (settings.forceSuggestions
                                        ? ' enabled'
                                        : '')
                                }
                                title='Save suggestions instead of translations'
                                onClick={this.toggleSetting('forceSuggestions')}
                            >
                                {'<glyph></glyph>Make Suggestions'}
                            </li>
                        </Localized>

                        <li className='horizontal-separator'></li>
                        <li>
                            <Localized id='editor-EditorSettings--change-all'>
                                <a href='/settings/'>{'Change All Settings'}</a>
                            </Localized>
                        </li>
                    </ul>
                )}
            </div>
        );
    }
}

export default onClickOutside(EditorSettingsBase);

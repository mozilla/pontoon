/* @flow */

import * as React from 'react';
import onClickOutside from 'react-onclickoutside';
import { Localized } from 'fluent-react';

import './KeyboardShortcuts.css';


type Props = null;


type State = {|
    visible: boolean,
|};


/*
 * Shows a list of keyboard shortcuts.
 */
export class EditorSettingsBase extends React.Component<Props, State> {
    constructor() {
        super();
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
    // when a user clicks outside the keyboard shortcut overlay.
    handleClickOutside = () => {
        this.setState({
            visible: false,
        });
    }

    render() {
        return <div className="keyboard-shortcuts">
            <Localized
                id="editor-keyboard-shortcuts-button"
                attrs={{ title: true }}
            >
                <div
                    className="selector far fa-keyboard"
                    title="Keyboard Shortcuts"
                    onClick={ this.toggleVisibility }
                />
            </Localized>

            { !this.state.visible ? null :
            <div
                className="overlay"
                onClick={ this.toggleVisibility }
            >
                <Localized id="editor-keyboard-shortcuts-overlay-title">
                    <h2>Keyboard Shortcuts</h2>
                </Localized>
                <table>
                    <tbody>
                        <tr>
                            <Localized id="editor-keyboard-shortcuts-save-translation">
                                <td>Save Translation</td>
                            </Localized>
                            <td>
                                <Localized id="editor-keyboard-shortcuts-save-translation-shortcut">
                                    <span>Enter</span>
                                </Localized>
                            </td>
                        </tr>
                        <tr>
                            <Localized id="editor-keyboard-shortcuts-cancel-translation">
                                <td>Cancel Translation</td>
                            </Localized>
                            <td>
                                <Localized id="editor-keyboard-shortcuts-cancel-translation-shortcut">
                                    <span>Esc</span>
                                </Localized>
                            </td>
                        </tr>
                        <tr>
                            <Localized id="editor-keyboard-shortcuts-insert-a-new-line">
                                <td>Insert A New Line</td>
                            </Localized>
                            <td>
                                <Localized
                                    id="editor-keyboard-shortcuts-insert-a-new-line-shortcut"
                                    mod1={ <span/> }
                                    accel={ <span/> }
                                >
                                    { '<mod1>Shift</mod1> + <accel>Enter</accel>' }
                                </Localized>
                            </td>
                        </tr>
                        <tr>
                            <Localized
                                id="editor-keyboard-shortcuts-go-to-next-string"
                            >
                                <td>Go To Next String</td>
                            </Localized>
                            <td>
                                <Localized
                                    id="editor-keyboard-shortcuts-go-to-next-string-shortcut"
                                    mod1={ <span/> }
                                    accel={ <span/> }
                                >
                                    { '<mod1>Alt</mod1> + <accel>Down</accel>' }
                                </Localized>
                            </td>
                        </tr>
                        <tr>
                            <Localized
                                id="editor-keyboard-shortcuts-go-to-previous-string">
                                <td>Go To Previous String</td>
                            </Localized>
                            <td>
                                <Localized
                                    id="editor-keyboard-shortcuts-go-to-previous-string-shortcut"
                                    mod1={ <span/> }
                                    accel={ <span/> }
                                >
                                    { '<mod1>Alt</mod1> + <accel>Up</accel>' }
                                </Localized>
                            </td>
                        </tr>
                        <tr>
                            <Localized
                                id="editor-keyboard-shortcuts-copy-from-source">
                                <td>Copy From Source</td>
                            </Localized>
                            <td>
                                <Localized
                                    id="editor-keyboard-shortcuts-copy-from-source-shortcut"
                                    mod1={ <span/> }
                                    mod2={ <span/> }
                                    accel={ <span/> }
                                >
                                    { '<mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>C</accel>' }
                                </Localized>
                            </td>
                        </tr>
                        <tr>
                            <Localized id="editor-keyboard-shortcuts-clear-translation">
                                <td>Clear Translation</td>
                            </Localized>
                            <td>
                                <Localized
                                    id="editor-keyboard-shortcuts-clear-translation-shortcut"
                                    mod1={ <span/> }
                                    mod2={ <span/> }
                                    accel={ <span/> }
                                >
                                    { '<mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>Backspace</accel>' }
                                </Localized>
                            </td>
                        </tr>
                        <tr>
                            <Localized id="editor-keyboard-shortcuts-search-strings">
                                <td>Search Strings</td>
                            </Localized>
                            <td>
                                <Localized
                                    id="editor-keyboard-shortcuts-search-strings-shortcut"
                                    mod1={ <span/> }
                                    mod2={ <span/> }
                                    accel={ <span/> }
                                >
                                    { '<mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>F</accel>' }
                                </Localized>
                            </td>
                        </tr>
                        <tr>
                            <Localized id="editor-keyboard-shortcuts-select-all-strings">
                                <td>Select All Strings</td>
                            </Localized>
                            <td>
                                <Localized
                                    id="editor-keyboard-shortcuts-select-all-strings-shortcut"
                                    mod1={ <span/> }
                                    mod2={ <span/> }
                                    accel={ <span/> }
                                >
                                    { '<mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>A</accel>' }
                                </Localized>
                            </td>
                        </tr>
                        <tr>
                            <Localized id="editor-keyboard-shortcuts-copy-from-helpers">
                                <td>Copy From Helpers</td>
                            </Localized>
                            <td>
                                <Localized id="editor-keyboard-shortcuts-copy-from-helpers-shortcut">
                                    <span>Tab</span>
                                </Localized>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            }
        </div>;
    }
}

export default onClickOutside(EditorSettingsBase);

/* @flow */

import * as React from 'react';

import './RichTranslationForm.css';

import { fluent } from 'core/utils';

import type { EditorProps } from 'core/editor';


/**
 * Render an Rich editor for Fluent string editting.
 */
export default class RichTranslationForm extends React.Component<EditorProps> {
    getMessage() {
        if (!this.props.editor.translation) {
            return fluent.getEmptyMessage(
                fluent.parser.parseEntry(
                    this.props.entity.original
                )
            );
        }

        return fluent.parser.parseEntry(this.props.editor.translation);
    }

    createHandleChange = (path: Array<string | number>) => {
        return (event: SyntheticInputEvent<HTMLTextAreaElement>) => {
            const value = event.currentTarget.value;

            const message = this.getMessage();

            let dest = message;
            // Walk the path until the next to last item.
            for (let i = 0, ln = path.length; i < ln - 1; i++) {
                dest = dest[path[i]];
            }
            // Assign the new value to the last element in the path, so that
            // it is actually assigned to the message object reference and
            // to the extracted value.
            dest[path[path.length - 1]] = value;

            this.props.updateTranslation(fluent.serializer.serializeEntry(message));
        }
    }

    renderElements(
        elements: Array<Object>,
        path: Array<string | number>,
        label: string,
        noValues: boolean
    ): Array<React.Node> {
        return elements.map((element, index) => {
            if (element.type === 'TextElement') {
                return <tr key={ `message-value-${index}` }>
                    <td>
                        <label htmlFor={ `message-value-${index}` }>{ label }</label>
                    </td>
                    <td>
                        <textarea
                            id={ `message-value-${index}` }
                            className=""
                            value={ noValues ? '' : element.value }
                            onChange={ this.createHandleChange([].concat(path, [ index, 'value' ])) }
                        />
                    </td>
                </tr>;
            }

            return null;
        })
    }

    render() {
        const message = this.getMessage();
        const noValues = !this.props.editor.translation;

        return <div className="fluent-rich-translation-form">
            <table>
                <tbody>
                    { (!message.value) ? null :
                        this.renderElements(message.value.elements, [ 'value', 'elements' ], 'Value', noValues)
                    }
                    { (!message.attributes) ? null :
                        message.attributes.map((attribute, index) => {
                            if (attribute.value) {
                                return this.renderElements(attribute.value.elements, [ 'attributes', index, 'value', 'elements' ], attribute.id.name, noValues)
                            }
                            return null;
                        })
                    }
                </tbody>
            </table>
        </div>;
    }
}

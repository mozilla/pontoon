/* @flow */

export type Variant = {
    default: boolean,
    key: string,
    value: FluentValue,
};

export type SelectExpression = {
    type: string,
    variants: Array<Variant>,
};

export type Placeable = {
    type: string,
    expression: SelectExpression,
}

export type PatternElement = {|
    type: string,
    value: string,
|} | Placeable;

export type FluentValue = {
    elements: Array<PatternElement>,
};

export type FluentAttribute = {
    id: { name: string },
    value: FluentValue,
};

export type FluentAttributes = Array<FluentAttribute>;

export type FluentMessage = {
    type: string,
    value: FluentValue,
    attributes: ?FluentAttributes,
    clone: () => FluentMessage,
    equals: (any) => boolean,
};


// Type of syntax of the translation to show in the editor.
// `simple` => SimpleEditor (the message can be simplified to a single text element)
// `rich` => RichEditor (the message can be displayed in our rich interface)
// `complex` => SourceEditor (the message is not supported by other editor types)
export type SyntaxType = 'simple' | 'rich' | 'complex';

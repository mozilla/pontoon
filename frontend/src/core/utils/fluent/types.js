/* @flow */

export type Variant = {
    default: boolean,
    key: string,
    value: Pattern,
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

export type Pattern = {
    elements: Array<PatternElement>,
};

export type FluentAttribute = {
    id: { name: string },
    value: Pattern,
};

export type FluentAttributes = Array<FluentAttribute>;

export type Entry = {
    type: string,
    value: Pattern,
    attributes: ?FluentAttributes,
    clone: () => Entry,
    equals: (any) => boolean,
};


// Type of syntax of the translation to show in the editor.
// `simple` => SimpleEditor (the message can be simplified to a single text element)
// `rich` => RichEditor (the message can be displayed in our rich interface)
// `complex` => SourceEditor (the message is not supported by other editor types)
export type SyntaxType = 'simple' | 'rich' | 'complex';

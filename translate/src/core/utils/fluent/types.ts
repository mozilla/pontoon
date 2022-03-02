// Type of syntax of the translation to show in the editor.
// `simple` => SimpleEditor (the message can be simplified to a single text element)
// `rich` => RichEditor (the message can be displayed in our rich interface)
// `complex` => SourceEditor (the message is not supported by other editor types)
export type SyntaxType = 'simple' | 'rich' | 'complex';

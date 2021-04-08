/* @flow */

declare module '@fluent/bundle' {
    declare export class FluentResource {
        constructor(source: string): this;
    }
    declare export type TextTransform = (text: string) => string;
    declare export class FluentBundle {
        constructor(
            locales: string | Array<string>,
            opts?: {
                useIsolating?: boolean,
                transform?: TextTransform,
            },
        ): this;
        addResource(
            res: FluentResource,
            opts?: {
                allowOverrides?: boolean,
            },
        ): Array<Error>;
    }
}

declare module '@fluent/langneg' {
    declare interface NegotiateLanguagesOptions {
        strategy?: 'filtering' | 'matching' | 'lookup';
        defaultLocale?: string;
    }
    declare export function negotiateLanguages(
        requestedLocales: $ReadOnlyArray<string>,
        availableLocales: $ReadOnlyArray<string>,
        opts?: NegotiateLanguagesOptions,
    ): Array<string>;
}

declare module '@fluent/react' {
    declare export class ReactLocalization {
        constructor(Array<any>): ReactLocalization;
    }

    declare export function LocalizationProvider(
        props: any,
    ): React$Element<any>;

    declare export interface LocalizedProps {
        id: string;
        attrs?: { [string]: boolean };
        children?: React$Node;
        vars?: { [string]: any };
        elems?: { [string]: ?React$Element<any> };
    }
    declare export function Localized(
        props: LocalizedProps,
    ): React$Element<any>;
}

declare module '@fluent/syntax' {
    declare export class BaseNode {
        [name: string]: mixed;
        equals(other: BaseNode, ignoredFields?: Array<string>): boolean;
        clone(): this;
    }
    declare export class SyntaxNode extends BaseNode {
        span?: Span;
        addSpan(start: number, end: number): void;
    }
    declare export class Resource extends SyntaxNode {
        type: 'Resource';
        body: Array<Entry>;
        constructor(body?: Array<Entry>): this;
    }
    declare export type Entry = Message | Term | Comments | Junk;
    declare export class Message extends SyntaxNode {
        type: 'Message';
        id: Identifier;
        value: Pattern | null;
        attributes: Array<Attribute>;
        comment: Comment | null;
        constructor(
            id: Identifier,
            value?: Pattern | null,
            attributes?: Array<Attribute>,
            comment?: Comment | null,
        ): this;
    }
    declare export class Term extends SyntaxNode {
        type: 'Term';
        id: Identifier;
        value: Pattern;
        attributes: Array<Attribute>;
        comment: Comment | null;
        constructor(
            id: Identifier,
            value: Pattern,
            attributes?: Array<Attribute>,
            comment?: Comment | null,
        ): this;
    }
    declare export class Pattern extends SyntaxNode {
        type: 'Pattern';
        elements: Array<PatternElement>;
        constructor(elements: Array<PatternElement>): this;
    }
    declare export type PatternElement = TextElement | Placeable;
    declare export class TextElement extends SyntaxNode {
        type: 'TextElement';
        value: string;
        constructor(value: string): this;
    }
    declare export class Placeable extends SyntaxNode {
        type: 'Placeable';
        expression: Expression;
        constructor(expression: Expression): this;
    }
    /**
     * A subset of expressions which can be used as outside of Placeables.
     */
    declare export type InlineExpression =
        | StringLiteral
        | NumberLiteral
        | FunctionReference
        | MessageReference
        | TermReference
        | VariableReference
        | Placeable;
    declare export type Expression = InlineExpression | SelectExpression;
    declare export class BaseLiteral extends SyntaxNode {
        value: string;
        constructor(value: string): this;
        parse(): {
            value: any,
        };
    }
    declare export class StringLiteral extends BaseLiteral {
        type: 'StringLiteral';
        parse(): {
            value: string,
        };
    }
    declare export class NumberLiteral extends BaseLiteral {
        type: 'NumberLiteral';
        parse(): {
            value: number,
            precision: number,
        };
    }
    declare export type Literal = StringLiteral | NumberLiteral;
    declare export class MessageReference extends SyntaxNode {
        type: 'MessageReference';
        id: Identifier;
        attribute: Identifier | null;
        constructor(id: Identifier, attribute?: Identifier | null): this;
    }
    declare export class TermReference extends SyntaxNode {
        type: 'TermReference';
        id: Identifier;
        attribute: Identifier | null;
        arguments: CallArguments | null;
        constructor(
            id: Identifier,
            attribute?: Identifier | null,
            args?: CallArguments | null,
        ): this;
    }
    declare export class VariableReference extends SyntaxNode {
        type: 'VariableReference';
        id: Identifier;
        constructor(id: Identifier): this;
    }
    declare export class FunctionReference extends SyntaxNode {
        type: 'FunctionReference';
        id: Identifier;
        arguments: CallArguments;
        constructor(id: Identifier, args: CallArguments): this;
    }
    declare export class SelectExpression extends SyntaxNode {
        type: 'SelectExpression';
        selector: InlineExpression;
        variants: Array<Variant>;
        constructor(selector: InlineExpression, variants: Array<Variant>): this;
    }
    declare export class CallArguments extends SyntaxNode {
        type: 'CallArguments';
        positional: Array<InlineExpression>;
        named: Array<NamedArgument>;
        constructor(
            positional?: Array<InlineExpression>,
            named?: Array<NamedArgument>,
        ): this;
    }
    declare export class Attribute extends SyntaxNode {
        type: 'Attribute';
        id: Identifier;
        value: Pattern;
        constructor(id: Identifier, value: Pattern): this;
    }
    declare export class Variant extends SyntaxNode {
        type: 'Variant';
        key: Identifier | NumberLiteral;
        value: Pattern;
        default: boolean;
        constructor(
            key: Identifier | NumberLiteral,
            value: Pattern,
            def: boolean,
        ): this;
    }
    declare export class NamedArgument extends SyntaxNode {
        type: 'NamedArgument';
        name: Identifier;
        value: Literal;
        constructor(name: Identifier, value: Literal): this;
    }
    declare export class Identifier extends SyntaxNode {
        type: 'Identifier';
        name: string;
        constructor(name: string): this;
    }
    declare export class BaseComment extends SyntaxNode {
        content: string;
        constructor(content: string): this;
    }
    declare export class Comment extends BaseComment {
        type: 'Comment';
    }
    declare export class GroupComment extends BaseComment {
        type: 'GroupComment';
    }
    declare export class ResourceComment extends BaseComment {
        type: 'ResourceComment';
    }
    declare export type Comments = Comment | GroupComment | ResourceComment;
    declare export class Junk extends SyntaxNode {
        type: 'Junk';
        annotations: Array<Annotation>;
        content: string;
        constructor(content: string): this;
        addAnnotation(annotation: Annotation): void;
    }
    declare export class Span extends BaseNode {
        type: 'Span';
        start: number;
        end: number;
        constructor(start: number, end: number): this;
    }
    declare export class Annotation extends SyntaxNode {
        type: 'Annotation';
        code: string;
        arguments: Array<mixed>;
        message: string;
        constructor(code: string, args: mixed[] | void, message: string): this;
    }

    /**
     * Parsers
     */
    declare export interface FluentParserOptions {
        withSpans?: boolean;
    }
    declare export class FluentParser {
        withSpans: boolean;
        constructor(opts?: FluentParserOptions): this;
        parse(source: string): Resource;
        parseEntry(source: string): Entry;
    }

    /**
     * Serializers
     */
    declare export interface FluentSerializerOptions {
        withJunk?: boolean;
    }
    declare export class FluentSerializer {
        withJunk: boolean;
        constructor(opts?: FluentSerializerOptions): this;
        serialize(resource: Resource): string;
        serializeEntry(entry: Entry, state?: number): string;
    }
    declare export function serializeExpression(
        expr: Expression | Placeable,
    ): string;
    declare export function serializeVariantKey(
        key: Identifier | NumberLiteral,
    ): string;

    /**
     * A read-and-write visitor.
     *
     * Subclasses can be used to modify an AST in-place.
     *
     * To handle specific node types add methods like `visitPattern`.
     * Then, to descend into children call `genericVisit`.
     *
     * Visiting methods must implement the following interface:
     *
     *     interface TransformingMethod {
     *         (this: Transformer, node: BaseNode): BaseNode | void;
     *     }
     *
     * The returned node will replace the original one in the AST. Return
     * `undefined` to remove the node instead.
     */
    declare export class Transformer {
        [prop: string]: mixed;
        visit(node: BaseNode): BaseNode | void;
        genericVisit(node: BaseNode): BaseNode;
        +visitResource?: (node: Resource) => BaseNode | void;
        +visitMessage?: (node: Message) => BaseNode | void;
        +visitTerm?: (node: Term) => BaseNode | void;
        +visitPattern?: (node: Pattern) => BaseNode | void;
        +visitTextElement?: (node: TextElement) => BaseNode | void;
        +visitPlaceable?: (node: Placeable) => BaseNode | void;
        +visitStringLiteral?: (node: StringLiteral) => BaseNode | void;
        +visitNumberLiteral?: (node: NumberLiteral) => BaseNode | void;
        +visitMessageReference?: (node: MessageReference) => BaseNode | void;
        +visitTermReference?: (node: TermReference) => BaseNode | void;
        +visitVariableReference?: (node: VariableReference) => BaseNode | void;
        +visitFunctionReference?: (node: FunctionReference) => BaseNode | void;
        +visitSelectExpression?: (node: SelectExpression) => BaseNode | void;
        +visitCallArguments?: (node: CallArguments) => BaseNode | void;
        +visitAttribute?: (node: Attribute) => BaseNode | void;
        +visitVariant?: (node: Variant) => BaseNode | void;
        +visitNamedArgument?: (node: NamedArgument) => BaseNode | void;
        +visitIdentifier?: (node: Identifier) => BaseNode | void;
        +visitComment?: (node: Comment) => BaseNode | void;
        +visitGroupComment?: (node: GroupComment) => BaseNode | void;
        +visitResourceComment?: (node: ResourceComment) => BaseNode | void;
        +visitJunk?: (node: Junk) => BaseNode | void;
        +visitSpan?: (node: Span) => BaseNode | void;
        +visitAnnotation?: (node: Annotation) => BaseNode | void;
    }
}

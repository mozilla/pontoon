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

declare module 'react-content-marker' {
    declare export type TagFunction = (input: string) => React$Element<any>;
    declare export interface Parser {
        rule: string | RegExp;
        tag: TagFunction;
        matchIndex?: number;
    }
    declare export default function createMarker(parsers: Array<Parser>): any;
    declare export function mark(
        content: string | Array<React$Node>,
        rule: string | RegExp,
        tag: TagFunction,
        matchIndex?: number,
    ): Array<React$Node>;
}

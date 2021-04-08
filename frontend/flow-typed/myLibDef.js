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

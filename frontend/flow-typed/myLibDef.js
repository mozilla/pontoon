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

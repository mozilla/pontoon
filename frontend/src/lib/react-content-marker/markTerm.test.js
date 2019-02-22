import React from 'react';

import markTerm from './markTerm';


describe('markTerm', () => {
    it('correctly marks several strings in the content', () => {
        const content = 'A horse, a horse, my kingdom for a horse.';

        const res = markTerm(content, 'horse', x => <mark>{x}</mark>);
        const expected = [
            'A ',
            <mark>{ 'horse' }</mark>,
            ', a ',
            <mark>{ 'horse' }</mark>,
            ', my kingdom for a ',
            <mark>{ 'horse' }</mark>,
            '.',
        ];
        expect(res).toEqual(expected);
    });

    it('correctly marks a string at the beginning of the content', () => {
        const content = 'A horse, a horse, my kingdom for a horse.';

        const res = markTerm(content, 'A', x => <mark>{x}</mark>);
        const expected = [
            <mark>{ 'A' }</mark>,
            ' horse, a horse, my kingdom for a horse.',
        ];
        expect(res).toEqual(expected);
    });

    it('correctly marks a string at the end of the content', () => {
        const content = 'A horse, a horse, my kingdom for a horse.';

        const res = markTerm(content, 'horse.', x => <mark>{x}</mark>);
        const expected = [
            'A horse, a horse, my kingdom for a ',
            <mark>{ 'horse.' }</mark>,
        ];
        expect(res).toEqual(expected);
    });

    it('correctly marks the entire content', () => {
        const content = 'horse';

        const res = markTerm(content, 'horse', x => <mark>{x}</mark>);
        const expected = [
            <mark>{ 'horse' }</mark>,
        ];
        expect(res).toEqual(expected);
    });

    it('supports attributes in tag', () => {
        const content = 'word';

        const res = markTerm(
            content, content, x => <mark title='Word Finder'>{x}</mark>
        );

        const expected = [
            <mark title='Word Finder'>{ 'word' }</mark>,
        ];
        expect(res).toEqual(expected);
    });

    it('returns the input as an array if there is no match', () => {
        const content = 'A horse, a horse, my kingdom for a horse.';

        const res = markTerm(content, 'missing', x => <mark>{x}</mark>);

        const expected = [content];
        expect(res).toEqual(expected);
    });
});

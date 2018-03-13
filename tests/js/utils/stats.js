
import {AggregateStats, Stats} from 'utils/stats';


test('Stats constructor', () => {
    let stats = new Stats(
        {approved_strings: 7,
         fuzzy_strings: 11,
         translated_strings: 13,
         total_strings: 43});
    expect(stats.fuzzyStrings).toBe(11);
    expect(stats.missingStrings).toBe(12);
    expect(stats.suggestedStrings).toBe(13);
    expect(stats.totalStrings).toBe(43);
    expect(stats.translatedStrings).toBe(7);

    expect(stats.approvedPercent).toBe(16);
    expect(stats.fuzzyShare).toBe(26);
    expect(stats.missingShare).toBe(28);
    expect(stats.suggestedShare).toBe(30);
    expect(stats.translatedShare).toBe(16);
})


test('Stats constructor some zeros', () => {
    let stats = new Stats(
        {approved_strings: 0,
         fuzzy_strings: 0,
         translated_strings: 13,
         total_strings: 43});
    expect(stats.fuzzyStrings).toBe(0);
    expect(stats.missingStrings).toBe(30);
    expect(stats.suggestedStrings).toBe(13);
    expect(stats.totalStrings).toBe(43);
    expect(stats.translatedStrings).toBe(0);

    expect(stats.approvedPercent).toBe(0);
    expect(stats.fuzzyShare).toBe(0);
    expect(stats.missingShare).toBe(70);
    expect(stats.suggestedShare).toBe(30);
    expect(stats.translatedShare).toBe(0);
})


test('Stats constructor defaults', () => {
    let stats = new Stats()
    expect(stats.fuzzyStrings).toBe(0);
    expect(stats.missingStrings).toBe(0);
    expect(stats.totalStrings).toBe(0);
    expect(stats.suggestedStrings).toBe(0);
    expect(stats.translatedStrings).toBe(0);

    expect(stats.approvedPercent).toBe(0);
    expect(stats.fuzzyShare).toBe(0);
    expect(stats.missingShare).toBe(0);
    expect(stats.suggestedShare).toBe(0);
    expect(stats.translatedShare).toBe(0);
})


test('Stats approved', () => {
    let stats = new Stats(
        {approved_strings: 1337, fuzzy_strings: 723, total_strings: 5000});
    expect(stats.approvedPercent).toBe(
        parseInt(
            Math.floor(
                1337 / parseFloat(5000) * 100)))
});


test('Stats shares', () => {
    let stats = new Stats(
        {approved_strings: 1337, fuzzy_strings: 723, total_strings: 5000});
    expect(stats.fuzzyShare).toBe(Math.round(723 / parseFloat(5000) * 100));
});


test('AggregateStats constructor', () => {
    const data = [
        {approved_strings: 7,
         fuzzy_strings: 11,
         translated_strings: 13,
         total_strings: 43},
        {approved_strings: 23,
         fuzzy_strings: 17,
         translated_strings: 19,
         total_strings: 31}]
    let stats = new AggregateStats(data);
    expect(stats instanceof Stats).toBe(true);
    expect(stats.fuzzyStrings).toBe(28);
    expect(stats.suggestedStrings).toBe(32);
    expect(stats.totalStrings).toBe(74);
    expect(stats.translatedStrings).toBe(30);
});

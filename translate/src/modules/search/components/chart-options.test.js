import { getChartOptions } from './chart-options';

describe('getChartOptions', () => {
  afterEach(() => {
    document.body.style.removeProperty('--status-translated');
  });

  it('reads the current value of theme CSS variables', () => {
    document.body.style.setProperty('--status-translated', '#111111');
    expect(getChartOptions([], () => {}).navigator.series.color).toBe(
      '#111111',
    );

    document.body.style.setProperty('--status-translated', '#222222');
    expect(getChartOptions([], () => {}).navigator.series.color).toBe(
      '#222222',
    );
  });

  it('includes the given data and setExtremes handler', () => {
    const data = [[1, 2]];
    const setExtremes = () => {};
    const options = getChartOptions(data, setExtremes);

    expect(options.series[0].data).toBe(data);
    expect(options.xAxis[0].events.setExtremes).toBe(setExtremes);
  });
});

import React, { useCallback, useEffect, useRef, useState } from 'react';

import date from 'date-and-time';
import { Localized } from '@fluent/react';

import Highcharts from 'highcharts/highstock';
import highchartsStock from 'highcharts/modules/stock';
import HighchartsReact from 'highcharts-react-official';

import type { TimeRangeType } from '..';
import { CHART_OPTIONS } from './chart-options';

import './TimeRangeFilter.css';
import classNames from 'classnames';

const INPUT_FORMAT = 'DD/MM/YYYY HH:mm';
const URL_FORMAT = 'YYYYMMDDHHmm';

type Props = {
  project: string;
  timeRange: TimeRangeType | null;
  timeRangeData: Array<Array<number>>;
  applySingleFilter: (value: string, filter: 'timeRange') => void;
  setTimeRange: (value: string | null) => void;
};

const asTime = (n: number) => date.parse(String(n), URL_FORMAT, true).getTime();

function getTimeForInput(urlTime: number | null) {
  if (!urlTime) {
    return '';
  }
  const d = date.parse(urlTime.toString(), URL_FORMAT, true);
  return isNaN(Number(d)) ? urlTime.toString() : date.format(d, INPUT_FORMAT);
}

function getTimeForURL(unixTime: number) {
  const d = new Date(unixTime);
  return parseInt(date.format(d, URL_FORMAT, true));
}

/**
 * Shows a Time Range filter panel.
 */
export function TimeRangeFilter({
  project,
  timeRange,
  timeRangeData,
  applySingleFilter,
  setTimeRange,
}: Props): React.ReactElement | null {
  const chart = useRef<HighchartsReact>(null);
  const [chartFrom, setChartFrom] = useState<number | null>(null);
  const [chartTo, setChartTo] = useState<number | null>(null);
  const [chartOptions, setChartOptions] = useState<{
    series: { data: unknown[] }[];
    xAxis: {
      events: {
        setExtremes: ((arg0: { min: number; max: number }) => void) | null;
      };
    }[];
  }>(CHART_OPTIONS);
  const [inputFrom, setInputFrom] = useState('');
  const [inputTo, setInputTo] = useState('');
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Initialize the highchartsStock module
    highchartsStock(Highcharts);

    // Set global options
    Highcharts.setOptions({ lang: { rangeSelectorZoom: '' } });

    // Set the callback function that fires when the minimum and maximum is set for the axis,
    // either by calling the .setExtremes() method or by selecting an area in the chart.
    chartOptions.xAxis[0].events.setExtremes = ({ min, max }) => {
      const chartFrom = getTimeForURL(min);
      const chartTo = getTimeForURL(max);

      setChartFrom(chartFrom);
      setChartTo(chartTo);
      setInputFrom(getTimeForInput(chartFrom));
      setInputTo(getTimeForInput(chartTo));
    };
  }, []);

  useEffect(() => {
    // In case of no translations
    if (timeRangeData.length === 0) {
      return;
    }

    // Set chart boundaries from the URL parameter if given,
    // else use default chart boundaries (full chart)
    const chartFrom = timeRange?.from ?? getTimeForURL(timeRangeData[0][0]);
    const chartTo =
      timeRange?.to ??
      getTimeForURL(timeRangeData[timeRangeData.length - 1][0]);

    setChartFrom(chartFrom);
    setChartTo(chartTo);
    setInputFrom(getTimeForInput(chartFrom));
    setInputTo(getTimeForInput(chartTo));

    setChartOptions({
      ...chartOptions,
      series: [{ data: timeRangeData }, ...chartOptions.series.slice(1)],
    });
  }, [timeRangeData]);

  useEffect(() => {
    if (chartFrom && chartTo) {
      chart.current?.chart.xAxis[0].setExtremes(
        asTime(chartFrom),
        asTime(chartTo),
      );
    }
  }, [visible]);

  useEffect(() => {
    // When filters are toggled or applied, we update the filters state in the SearchBox
    // component, so that we can request entities accordingly. But the Time Range filter
    // state also changes when chartFrom and chartTo values change, so when that happens,
    // we also need to propagate changes to the SearchBox state.
    // Without this code, if you have Time Range filter applied and then change range and
    // click the Apply Filter button, nothing happens. As described in bug 1469611.
    if (timeRange) {
      setTimeRange([chartFrom, chartTo].join('-'));
    }
  }, [chartFrom, chartTo]);

  const isValidInput = (value: string) => date.isValid(value, INPUT_FORMAT);

  const handleInputChange = useCallback(
    (ev: React.SyntheticEvent<HTMLInputElement>) => {
      const { name, value } = ev.currentTarget;
      const isFrom = name === 'From';
      const isTo = name === 'To';

      if (isValidInput(value) && chartFrom && chartTo) {
        const time = date.parse(value, INPUT_FORMAT).getTime();
        const from = isFrom ? time : asTime(chartFrom);
        const to = isTo ? time : asTime(chartTo);
        chart.current?.chart.xAxis[0].setExtremes(from, to);
      }

      if (isFrom) {
        setInputFrom(value);
      } else if (isTo) {
        setInputTo(value);
      }
    },
    [chartFrom, chartTo],
  );

  const toggleEditingTimeRange = useCallback(
    (ev: React.MouseEvent) => {
      // After Save Range is clicked...
      if (visible) {
        // Make sure Time Range filter is selected
        if (!timeRange) {
          ev.stopPropagation();
          setTimeRange([chartFrom, chartTo].join('-'));
        }

        // Make sure inputs are in sync with chart
        setInputFrom(getTimeForInput(chartFrom));
        setInputTo(getTimeForInput(chartTo));
      }

      setVisible((prev) => !prev);
    },
    [chartFrom, chartTo, setTimeRange, timeRange, visible],
  );

  const toggleTimeRangeFilter = useCallback(
    (ev: React.MouseEvent) => {
      if (!visible) {
        ev.stopPropagation();
        setTimeRange(timeRange ? null : [chartFrom, chartTo].join('-'));
      }
    },
    [chartFrom, chartTo, setTimeRange, timeRange, visible],
  );

  const applyTimeRangeFilter = useCallback(() => {
    if (!visible) {
      applySingleFilter([chartFrom, chartTo].join('-'), 'timeRange');
    }
  }, [chartFrom, chartTo, visible]);

  // In case of no translations or the All Projects view
  if (timeRangeData.length === 0 || project === 'all-projects') {
    return null;
  }

  const timeRangeClass = classNames(
    'time-range clearfix',
    visible && 'editing',
    timeRange && 'selected',
  );

  return (
    <>
      <li className='horizontal-separator for-time-range'>
        <Localized id='search-TimeRangeFilter--heading-time'>
          <span>TRANSLATION TIME</span>
        </Localized>

        {!visible ? (
          <Localized
            id='search-TimeRangeFilter--edit-range'
            elems={{
              glyph: <i className='fas fa-chart-area' />,
            }}
          >
            <button onClick={toggleEditingTimeRange} className='edit-range'>
              {'<glyph></glyph>EDIT RANGE'}
            </button>
          </Localized>
        ) : (
          <Localized id='search-TimeRangeFilter--save-range'>
            <button onClick={toggleEditingTimeRange} className='save-range'>
              SAVE RANGE
            </button>
          </Localized>
        )}
      </li>
      <li className={timeRangeClass} onClick={applyTimeRangeFilter}>
        <span className='status fas' onClick={toggleTimeRangeFilter}></span>

        <span className='clearfix'>
          <label className='from'>
            From
            <input
              type='datetime'
              name='From'
              className={isValidInput(inputFrom) ? '' : 'error'}
              disabled={!visible}
              onChange={handleInputChange}
              value={inputFrom}
            />
          </label>
          <label className='to'>
            To
            <input
              type='datetime'
              name='To'
              className={isValidInput(inputTo) ? '' : 'error'}
              disabled={!visible}
              onChange={handleInputChange}
              value={inputTo}
            />
          </label>
        </span>

        {visible ? (
          <HighchartsReact
            highcharts={Highcharts}
            // @ts-expect-error
            options={chartOptions}
            constructorType={'stockChart'}
            allowChartUpdate={false}
            containerProps={{ className: 'chart' }}
            ref={chart}
          />
        ) : null}
      </li>
    </>
  );
}

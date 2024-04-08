import React from "react";
import { BatchInfo } from "../api/server";
import { BatchConfig } from "../model/problem";


export type BatchSummaryProps = {
  batchInfo: BatchInfo,
};

function resolveBatchName(batchConfig: BatchConfig): string {
  const outDir = batchConfig.outputDir;
  const stem = outDir?.split('/').at(-1);
  return stem ?? "undefined";
}

function parseStartTime(startTime?: string): string | undefined {
  if (!startTime) {
    return undefined;
  }
  const [date, time] = startTime.split('T', 2);
  const year = parseInt(date.slice(0, 2)) + 2000;
  const month = parseInt(date.slice(2, 4)) - 1;  // Numbered from 0-11
  const day = parseInt(date.slice(4, 6));
  const hour = parseInt(time.slice(0, 2));
  const minutes = parseInt(time.slice(2, 4));
  const seconds = parseInt(time.slice(4, 6));


  console.log(month);

  let d = new Date();
  d.setFullYear(year);
  d.setMonth(month);
  d.setDate(day);
  d.setHours(hour);
  d.setMinutes(minutes);
  d.setSeconds(seconds);
  return d.toLocaleString();
}


function BatchSummary({ batchInfo }: BatchSummaryProps): React.JSX.Element {
  // const batchName = resolveBatchName(batchInfo);
  const batchName = batchInfo.name;
  const experimentNames = batchInfo.config.configs.map(exp => exp.name).join(' ');
  console.log(batchInfo.name);
  const startTime = parseStartTime(batchInfo.config.startTime) ?? "Unknown";

  return (
    <div>
      <details>
        <summary>{batchName}</summary>
        Start time: {startTime},
        Experiments: {experimentNames}
      </details>
    </div>
  );
}

export default BatchSummary;

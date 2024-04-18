import React, { useState } from "react";
import { Oval } from "react-loader-spinner";
import { useNavigate } from "react-router-dom";
import { BatchInfo } from "../api/server";
import { useServer } from "../hooks/useServer";
import { BatchConfig } from "../model/problem";
import "./css/BatchSummary.css"


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

  let d = new Date();
  d.setFullYear(year);
  d.setMonth(month);
  d.setDate(day);
  d.setHours(hour);
  d.setMinutes(minutes);
  d.setSeconds(seconds);
  return d.toLocaleString();
}

type ProcessedStatusProps = {
  isProcessed?: boolean | null
};

function ProcessedStatus({ isProcessed }: ProcessedStatusProps): React.JSX.Element {
  const text = isProcessed == null ? 'Unknown' : isProcessed ? 'Yes' : 'No';
  const cssClass = isProcessed == null ? 'processed-unknown' : isProcessed ? 'processed-yes' : 'processed-no';

  function onClick(_event: React.MouseEvent<HTMLButtonElement>) {

  }

  return (
    <div>
      <div style={{ display: 'flex' }}>
        <span style={{ paddingRight: 4 }}>isProcessed:</span>
        <span className={cssClass}>{text}</span>
      </div>
    </div>
  )
}

function BatchSummary({ batchInfo }: BatchSummaryProps): React.JSX.Element {
  const navigate = useNavigate();
  const serverApi = useServer();

  const [isProcessingBatch, setIsProcessingBatch] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<string | undefined>(undefined);

  // const batchName = resolveBatchName(batchInfo);
  const batchName = batchInfo.name;
  const experimentNames = batchInfo.config.configs.map(exp => exp.name).sort().join(' ');
  const startTime = parseStartTime(batchInfo.config.startTime) ?? "Unknown";
  const solverType = batchInfo.config.solverConfig?.solverType ?? "Unknown";
  const nGenerations = batchInfo.config.solverConfig?.nGen ?? "Unknown";
  const isProcessed = batchInfo.isProcessed ?? null;
  const solvedCount = batchInfo.solvedCount ?? "Unknown";

  function navigateToDetails(_event: React.MouseEvent<HTMLButtonElement>) {
    // if (isProcessed) {
    //   navigate(`/details/${batchName}`);
    // }
    navigate(`/details/${batchName}`);
  }

  function onProcessButtonClick(_event: React.MouseEvent<HTMLButtonElement>) {
    setIsProcessingBatch(true);
    serverApi?.processBatch({ batchName: batchName })
      .then(response => {
        setIsProcessingBatch(false);
        setProcessingStatus(response?.error)
      })
      .catch(err => {
        setIsProcessingBatch(false);
        setProcessingStatus("Error while processing batch");
      })
  }

  return (
    <div className="batch-info-container">
      <div style={{ display: 'flex' }}>
        <div style={{ flex: 1 }}>
          <h2 style={{ fontWeight: 400, marginBottom: 4 }}>{batchName}</h2>
          <div key="start-time">Start time: {startTime}</div>
          <div key="experiments">Experiments: {experimentNames}</div>
          <div key="solved-count">Solved: {solvedCount} / {batchInfo.config.configs.length}</div>
          <div key="solver-type">Solver: {solverType}</div>
          <div key="generations">Generations: {nGenerations}</div>
          <ProcessedStatus isProcessed={isProcessed} key="processed" />
        </div>
        <div style={{ flex: 2 }}>
          <div>
            <button onClick={navigateToDetails}>Details</button>
          </div>
          {isProcessed === false && !isProcessingBatch && (
            <div>
              <button onClick={onProcessButtonClick}>Process</button>
            </div>
          )}
          {isProcessed === false && isProcessingBatch && (
            <Oval></Oval>
          )}
          {isProcessed === false && !isProcessingBatch && processingStatus !== undefined && (
            <div>{processingStatus}</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default BatchSummary;

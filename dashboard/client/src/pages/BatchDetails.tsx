import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Server, { TableRequest } from "../api/server";
import SummaryByExpTable, { SummaryByExpTableData } from "../components/tables/SummaryByExpTable";
import SummaryTotalTable, { SummaryTotalTableData } from "../components/tables/SummaryTotalTable";
import { useServer } from "../hooks/useServer";
import './css/BatchDetails.css';
import ConvergenceInfoTable, { ConvergenceInfoTableRowData } from "../components/tables/ConvergenceInfoTable";
import RunSummaryStatsTable, { RunInfoTableRowData as RunSummaryStatsTableRowData } from "../components/tables/RunSummaryStatsTable";

function createTableRequest(tableName: string, batchName: string): TableRequest {
  return {
    tableName: tableName,
    batchName: batchName,
  }
}

function requestCreatorFactory(batchName: string): (tableName: string) => TableRequest {
  return (tableName: string) => createTableRequest(tableName, batchName)
}

function tableRequester<ResponseT>(request: TableRequest, signal: AbortSignal, stateSetter: (res: ResponseT | null) => void, serverApi?: Server) {
  serverApi?.fetchTable(request, signal)
    .then(result => {
      if (result !== undefined) {
        stateSetter(result as ResponseT);
      } else {
        console.error("Received null response from server");
      }
    })
    .catch(err => {
      console.error(`Received error: ${err}`);
      stateSetter(null);
    })
}

function tableRequesterFactory(signal: AbortSignal, serverApi?: Server) {
  return <ResponseT, > (request: TableRequest, stateSetter: (res: ResponseT | null) => void) => {
    return tableRequester<ResponseT>(request, signal, stateSetter, serverApi);
  }
}

function BatchDetailsRoute(): React.JSX.Element {
  let { batchName } = useParams();
  const serverApi = useServer();

  const [summaryTotal, setSummaryTotal] = useState<SummaryTotalTableData | null>(null);
  const [summaryByExp, setSummaryByExp] = useState<SummaryByExpTableData | null>(null);
  const [convergenceInfo, setConvergenceInfo] = useState<ConvergenceInfoTableRowData[] | null>(null);
  const [runSummaryStats, setRunSummaryStats] = useState<RunSummaryStatsTableRowData[] | null>(null);

  useEffect(() => {
    const abortController = new AbortController();
    const requestCreator = requestCreatorFactory(batchName!);
    const tableRequester = tableRequesterFactory(abortController.signal, serverApi);

    async function fetchBatchDetails() {
      tableRequester(requestCreator('summary_total'), setSummaryTotal);
      tableRequester(requestCreator('summary_by_exp'), setSummaryByExp);
      tableRequester(requestCreator('convergence_info'), setConvergenceInfo);
      tableRequester(requestCreator('run_summary_stats'), setRunSummaryStats);
    }
    fetchBatchDetails();

    return () => {
      abortController.abort();
    }
  }, [serverApi, batchName]);

  const isLoaded = summaryByExp && summaryTotal;

  return (
    <div className="padded-left">
      <h1 className="top-title">{batchName}</h1>
      {isLoaded && (
        <SummaryTotalTable data={summaryTotal} />
      )}
      {isLoaded && (
        <SummaryByExpTable data={summaryByExp} />
      )}
      {isLoaded && convergenceInfo != null && (
        <ConvergenceInfoTable data={convergenceInfo} />
      )}
      {isLoaded && runSummaryStats != null && (
        <RunSummaryStatsTable data={runSummaryStats} />
      )}
    </div>
  );
}

export default BatchDetailsRoute;

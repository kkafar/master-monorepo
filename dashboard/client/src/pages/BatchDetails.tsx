import { useCallback, useEffect, useState } from "react";
import { SetURLSearchParams, useParams, useSearchParams } from "react-router-dom";
import Server, { BatchPlotsResponse, ExperimentPlots, TableRequest } from "../api/server";
import SummaryByExpTable, { SummaryByExpTableData } from "../components/tables/SummaryByExpTable";
import SummaryTotalTable, { SummaryTotalTableData } from "../components/tables/SummaryTotalTable";
import { useServer } from "../hooks/useServer";
import './css/BatchDetails.css';
import ConvergenceInfoTable, { ConvergenceInfoTableRowData } from "../components/tables/ConvergenceInfoTable";
import RunSummaryStatsTable, { RunInfoTableRowData as RunSummaryStatsTableRowData } from "../components/tables/RunSummaryStatsTable";
import TitledTable from "../components/TitledTable";

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
  return <ResponseT,>(request: TableRequest, stateSetter: (res: ResponseT | null) => void) => {
    return tableRequester<ResponseT>(request, signal, stateSetter, serverApi);
  }
}

type BatchHeaderProps = {
  batchName: string;
};

function BatchHeader(props: BatchHeaderProps): React.JSX.Element {
  const { batchName } = props;

  return (
    <h1 className="top-title">{batchName}</h1>
  );
}

type BatchDetailsNavigationProps = {
  activeTab: string;
  setSearchParams: SetURLSearchParams;
}

function BatchDetailsNavigation(props: BatchDetailsNavigationProps): React.JSX.Element {
  const {
    activeTab,
    setSearchParams
  } = props;

  function onTablesClicked(_event: React.MouseEvent<HTMLDivElement>) {
    setSearchParams(old => {
      old.set("activeTab", "tables");
      return old;
    })
  }

  function onPlotsClicked(_event: React.MouseEvent<HTMLDivElement>) {
    setSearchParams(old => {
      old.set("activeTab", "plots");
      return old;
    })
  }

  let tablesClass = "tab-button";
  let plotsClass = "tab-button";

  if (activeTab === "tables") {
    tablesClass += " active";
  } else {
    plotsClass += " active";
  }

  return (
    <div className="flexed topnav">
      <div className={tablesClass} onClick={onTablesClicked}>Tables</div>
      <div className={plotsClass} onClick={onPlotsClicked}>Plots</div>
    </div>
  );
}

type BatchDetailsTablesTabProps = {
  batchName: string
};

function BatchDetailsTablesTab({ batchName }: BatchDetailsTablesTabProps): React.JSX.Element {
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
    <div>
      {isLoaded && (
        <TitledTable tableComponentFactory={() => <SummaryTotalTable data={summaryTotal} />} />
      )}
      {isLoaded && (
        <TitledTable tableComponentFactory={() => <SummaryByExpTable data={summaryByExp} />} />
      )}
      {isLoaded && convergenceInfo != null && (
        <TitledTable tableComponentFactory={() => <ConvergenceInfoTable data={convergenceInfo} />} />
      )}
      {isLoaded && runSummaryStats != null && (
        <TitledTable tableComponentFactory={() => <RunSummaryStatsTable data={runSummaryStats} />} />
      )}
    </div>
  );
}

type BatchDetailsPlotsTabProps = {
  batchName: string
};

type ExperimentPlotsDetailsProps = {
  expPlots: ExperimentPlots,
};

function ExpPlotsDetails({ expPlots }: ExperimentPlotsDetailsProps): React.JSX.Element {
  const imgSrcFactory = useCallback((base: string) => {
    let plotUrl = new URL(base);
    plotUrl.pathname = "assets" + plotUrl.pathname;
    return plotUrl.toString();
  }, []);

  return (
    <div>
      <details>
        <summary style={{ fontSize: '1.5rem' }}>{expPlots.expName}</summary>
        <div style={{ display: 'flex' }}>
          <div>
            <img src={imgSrcFactory(expPlots.fitAvg)} alt="Alt" />
          </div>
          <div>
            <img src={imgSrcFactory(expPlots.bestRun)} alt="Alt" />
          </div>
          {expPlots.bestRunFitAvg && (
            <div>
              <img src={imgSrcFactory(expPlots.bestRunFitAvg)} alt="Alt" />
            </div>
          )}
          {expPlots.popMet && (
            <div>
              <img src={imgSrcFactory(expPlots.popMet)} alt="Alt" />
            </div>
          )}
          {expPlots.solution && (
            <div>
              <img src={imgSrcFactory(expPlots.solution)} alt="Alt" />
            </div>
          )}
        </div>
      </details>
    </div>
  );
}

function BatchDetailsPlotsTab({ batchName }: BatchDetailsPlotsTabProps): React.JSX.Element {
  const server = useServer();
  const [plotUrls, setPlotUrls] = useState<BatchPlotsResponse | null>(null);


  useEffect(() => {
    const abortController = new AbortController();

    async function fetchPlotUrls() {
      server?.fetchBatchPlots({ batchName: batchName }, abortController.signal)
        .then(result => {
          if (result !== undefined) {
            setPlotUrls(result as BatchPlotsResponse);
          } else {
            console.error("Received null response from server");
          }
        })
        .catch(err => {
          console.error(`Received error: ${err}`);
          setPlotUrls(null);
        })
    }

    fetchPlotUrls()

    return () => {
      abortController.abort();
    }
  }, [batchName, server]);


  return (
    <div>
      <h1>Plots</h1>
      <div>
        {plotUrls && (
          plotUrls.expPlots.sort((a, b) => a.expName < b.expName ? -1 : 1).map((plots, i) => <ExpPlotsDetails key={i.toString()} expPlots={plots} />)
        )}
      </div>
    </div>
  );
}

function BatchDetailsRoute(): React.JSX.Element {
  const { batchName = "Unknown" } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get("activeTab") ?? "tables";

  console.log("Render batch details route");

  return (
    <div className="padded-left">
      <BatchDetailsNavigation activeTab={activeTab} setSearchParams={setSearchParams} />
      <BatchHeader batchName={batchName} />
      {activeTab === "tables" && (
        <BatchDetailsTablesTab batchName={batchName} />
      )}
      {activeTab === "plots" && (
        <BatchDetailsPlotsTab batchName={batchName} />
      )}
    </div>
  );
}

export default BatchDetailsRoute;

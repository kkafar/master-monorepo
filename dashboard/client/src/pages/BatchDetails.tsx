import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Server from "../api/server";
import SummaryByExpTable, { SummaryByExpTableData } from "../components/tables/SummaryByExpTable";
import SummaryTotalTable, { SummaryTotalTableData } from "../components/tables/SummaryTotalTable";
import { useServer } from "../hooks/useServer";
import './css/BatchDetails.css';

// function createTableFetcher(serverApi: Server | undefined, reque)

function BatchDetailsRoute(): React.JSX.Element {
  let { batchName } = useParams();
  const serverApi = useServer();

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [summaryTotal, setSummaryTotal] = useState<SummaryTotalTableData | null>(null);
  const [summaryByExp, setSummaryByExp] = useState<SummaryByExpTableData | null>(null);

  useEffect(() => {
    const abortController = new AbortController();

    async function fetchBatchDetails() {
      serverApi?.fetchTable({ tableName: 'summary_total', batchName: batchName! }, abortController.signal)
        .then(result => {
          if (result !== undefined) {
            setSummaryTotal(result as SummaryTotalTableData);
          } else {
            console.error("Received null response from server");
          }
        })
        .catch(err => {
          console.error(`Received error: ${err}`);
        })

      serverApi?.fetchTable({ tableName: 'summary_by_exp', batchName: batchName! }, abortController.signal)
        .then(result => {
          if (result !== undefined) {
            setSummaryByExp(result as SummaryByExpTableData);
          } else {
            console.error("Received null response from server");
          }
        })
        .catch(err => {
          console.error(`Received error: ${err}`);
        })
    }
    fetchBatchDetails();

    return () => {
      abortController.abort();
    }
  }, [serverApi]);

  const isLoaded = summaryByExp && summaryTotal;

  return (
    <div className="padded-left">
      <h1 className="top-title">{batchName}</h1>
      {isLoaded && (
        <SummaryTotalTable data={summaryTotal!} />
      )}
      {isLoaded && (
        <SummaryByExpTable data={summaryByExp!} />
      )}
    </div>
  );
}

export default BatchDetailsRoute;

import React, { useContext, useEffect, useState } from "react";
import { Oval } from "react-loader-spinner";
import { BatchInfo, BatchListResponse } from "../api/server";
import BatchSummary from "../components/BatchSummary";
import { useServer } from "../hooks/useServer";
import './css/Home.css';


function Home(): React.JSX.Element {
  const serverApi = useServer();
  const [batches, setBatches] = useState<BatchInfo[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const abortController = new AbortController();

    async function fetchBatches() {
      serverApi?.fetchBatches(abortController.signal)
        .then(result => {
          if (result !== undefined) {
            setBatches(result.batchInfo);
          } else {
            console.error("Received null reponse from server");
          }
          setIsLoading(false);
        })
        .catch(err => {
          console.error(`Received error: ${err}`);
          setBatches([]);
          setIsLoading(false);
        })
    }

    fetchBatches();

    return () => {
      abortController.abort();
    }
  }, [serverApi]);

  const displayBatchList = !isLoading && batches.length > 0;

  return (
    <div>
      <h1 className="padded-left top-title">Batches</h1>
      {isLoading && (
        <div className="padded-left">
          <Oval strokeWidth={5} />
        </div>
      )}
      {displayBatchList && (
        <div className="padded-left batch-list-container">
          {batches.sort((a, b) => (a.name < b.name) ? -1 : 1).map(info => <BatchSummary key={info.name} batchInfo={info} />)}
        </div>
      )}
      {!displayBatchList && (
        <div className="padded-left">
          Seems that there are no batches present...
          Make sure that the server was passed appropriate directory with batch results.
        </div>
      )}
    </div>
  );
}

export default Home;

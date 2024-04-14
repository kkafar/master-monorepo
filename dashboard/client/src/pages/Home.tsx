import React, { useContext, useEffect, useState } from "react";
import { BatchInfo, BatchListResponse } from "../api/server";
import BatchSummary from "../components/BatchSummary";
import { useServer } from "../hooks/useServer";
import './css/Home.css';


function Home(): React.JSX.Element {
  const serverApi = useServer();
  const [batches, setBatches] = useState<BatchInfo[]>([]);

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
        })
        .catch(err => {
          console.error(`Received error: ${err}`);
        })
    }

    fetchBatches();

    return () => {
      abortController.abort();
    }
  }, [serverApi]);

  const displayBatchList = batches.length > 0;

  return (
    <div>
      <h1 className="padded-left top-title">Batches</h1>
      {displayBatchList && (
        <div className="padded-left batch-list-container">
          {batches.sort((a, b) => (a.name < b.name) ? -1 : 1).map(info => <BatchSummary batchInfo={info} />)}
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

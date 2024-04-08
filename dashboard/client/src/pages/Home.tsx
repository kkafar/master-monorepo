import React, { useContext, useEffect, useState } from "react";
import { BatchInfo, BatchListResponse } from "../api/server";
import BatchSummary from "../components/BatchSummary";
import ServerContext from "../contexts/ServerContext";
import { useServer } from "../hooks/useServer";


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
      // abortController.abort();
    }
  }, []);


  return (
    <div>
      <h1>Batches</h1>
      {batches.length > 0 && (
        <div>
          <ul>
            {batches.map(info => <BatchSummary batchInfo={info} />)}
          </ul>
        </div>
      )}
    </div>
  );
}

export default Home;

import React, { useContext, useEffect, useState } from "react";
import { BatchListResponse } from "../api/server";
import ServerContext from "../contexts/ServerContext";
import { useServer } from "../hooks/useServer";


function Home(): React.JSX.Element {
  const serverApi = useServer();
  const [batches, setBatches] = useState<string[]>([]);

  useEffect(() => {
    const abortController = new AbortController();

    async function fetchBatches() {
      const result = await serverApi?.fetchBatches(abortController.signal);
      if (result !== undefined) {
        setBatches(result.batchNames);
      }
    }

    fetchBatches();

    return () => {
      // abortController.abort();
    }
  }, []);


  return (
    <div>
      <div>Some Text</div>
      {batches.length > 0 && (
        batches.map(name => <div>{name}</div>)
      )}
    </div>
  );
}

export default Home;

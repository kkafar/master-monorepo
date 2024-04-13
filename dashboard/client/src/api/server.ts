import { BatchConfig } from "../model/problem";
import serverConfig from "../config/serverConfig.json"

export type BatchInfo = {
  name: string,
  config: BatchConfig,
}

export type BatchListResponse = {
  batchInfo: BatchInfo[];
}

class Server {
  baseUrl: string;
  endpoints: {
    batches: string,
  }

  constructor() {
    this.baseUrl = `http://localhost:${serverConfig.port}`;
    this.endpoints = {
      batches: this.baseUrl + '/batches',
    };
  }

  async fetchBatches(signal?: AbortSignal): Promise<BatchListResponse | undefined> {
    return fetch(this.endpoints.batches, { method: 'GET', signal: signal })
      .then(response => response.json())
      .catch(err => {
        console.error(`Error while fetching ${err}`)
      })
  }

}

export default Server;


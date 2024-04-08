import { BatchConfig } from "../model/problem";

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
    this.baseUrl = "http://localhost:8088";
    this.endpoints = {
      batches: this.baseUrl + '/batches',
    };
  }

  async fetchBatches(signal?: AbortSignal): Promise<BatchListResponse | undefined> {
    try {
      const response = await fetch(this.endpoints.batches, { method: 'GET', signal: signal });
      const parsedResponse = await response.json();
      console.log(parsedResponse);
      return parsedResponse;
    } catch (err) {
      console.error(`Error while fetching: ${err}`);
    }
    return undefined;
  }

}

export default Server;


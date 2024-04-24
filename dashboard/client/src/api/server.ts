import { BatchConfig } from "../model/problem";
import serverConfig from "../config/serverConfig.json"

export type BatchInfo = {
  name: string;
  solvedCount?: number;
  config: BatchConfig;
  isProcessed?: boolean;
}

export type BatchListResponse = {
  batchInfo: BatchInfo[];
}

export type TableRequest = {
  batchName: string;
  tableName: string;
};

export type TableResponse = {

};

export type ProcessRequest = {
  batchName: string;
  maxCpus?: number;
}

export type ProcessResponse = {
  error?: string;
}

class Server {
  baseUrl: string;
  endpoints: {
    batches: string,
    table: string,
    process: string,
  }

  constructor() {
    this.baseUrl = `http://localhost:${serverConfig.port}`;
    this.endpoints = {
      batches: this.baseUrl + '/batches',
      table: this.baseUrl + '/table',
      process: this.baseUrl + '/process'
    };
  }

  async fetchBatches(signal?: AbortSignal): Promise<BatchListResponse | undefined> {
    return fetch(this.endpoints.batches, { method: 'GET', signal: signal })
      .then(response => {
        if (response.status === 200) {
          return response.json();
        } else {
          throw response.json();
        }
      })
      .catch(err => {
        console.error(`[API] Error while fetching batches ${err}`);
        throw err;
      })
  }

  async fetchTable(request: TableRequest, signal?: AbortSignal): Promise<TableResponse | undefined> {
    const url = new URL(this.endpoints.table);
    url.searchParams.set("batchName", request.batchName);
    url.searchParams.set("tableName", request.tableName);

    return fetch(url, { method: 'GET', signal: signal })
      .then(response => {
        if (response.status === 200) {
          return response.json();
        } else {
          throw response.json();
        }
      })
      .catch(err => {
        console.error(`[API] Error while fetching table ${JSON.stringify(err)}`);
        throw err;
      })
  }

  async processBatch(request: ProcessRequest, signal?: AbortSignal): Promise<ProcessResponse | undefined> {
    const headers = new Headers();
    headers.set("Content-Type", "application/json");

    return fetch(this.endpoints.process, {
      method: 'POST',
      signal: signal,
      body: JSON.stringify(request),
      headers: headers,
    })
      .then(response => {
        if (response.status === 200) {
          return response.json();
        } else {
          throw response.json();
        }
      })
      .catch(err => {
        console.error(`[API] Error while processing batch ${request.batchName}: ${JSON.stringify(err)}`);
        throw err;
      })
  }
}

export default Server;


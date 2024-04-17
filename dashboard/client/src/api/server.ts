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

class Server {
  baseUrl: string;
  endpoints: {
    batches: string,
    table: string,
  }

  constructor() {
    this.baseUrl = `http://localhost:${serverConfig.port}`;
    this.endpoints = {
      batches: this.baseUrl + '/batches',
      table: this.baseUrl + '/table',
    };
  }

  async fetchBatches(signal?: AbortSignal): Promise<BatchListResponse | undefined> {
    return fetch(this.endpoints.batches, { method: 'GET', signal: signal })
      .then(response => response.json())
      .then(response => {
        console.log(response)
        return response;
      })
      .catch(err => {
        console.error(`Error while fetching batches ${err}`);
      })
  }

  async fetchTable(request: TableRequest, signal?: AbortSignal): Promise<TableResponse | undefined> {
    const url = new URL(this.endpoints.table);
    url.searchParams.set("batchName", request.batchName);
    url.searchParams.set("tableName", request.tableName);

    return fetch(url, { method: 'GET', signal: signal })
      .then(response => response.json())
      .then(response => {
        console.log(response);
        return response;
      })
      .catch(err => {
        console.error(`Error while fetching table ${err}`);
      })
  }

}

export default Server;


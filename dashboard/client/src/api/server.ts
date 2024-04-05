export type BatchListRequest = {

};

export type BatchListResponse = {
  batchNames: string[];
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
    const response = await fetch(this.endpoints.batches, { method: 'GET', signal: signal });
    const parsedResponse = await response.json();
    console.log(parsedResponse);
    return parsedResponse;
  }

}

export default Server;


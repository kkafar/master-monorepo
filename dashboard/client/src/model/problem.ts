export type InstanceInfo = {
  id: string,
  ref: string,
  jobs: number,
  machines: number,
  lower_bound: number,
  lower_bound_ref: string,
  best_solution: number,
  best_solution_ref: string,
  best_solution_time: string,
  best_solution_time_ref: string,
};

export type ExperimentConfig = {
  inputFile: string,
  outputDir: string,
  configFile?: string,
  nSeries: number,
};

export type Experiment = {
  name: string,
  instance: InstanceInfo,
  config: ExperimentConfig,
};

export type SolverConfig = {
  inputFile?: string,
  outputDir?: string,
  nGen: number,
  popSize?: number,
  delayConstFactor?: number,
  solverType?: string,
};

export type BatchConfig = {
  outputDir?: string,
  configs: Experiment[],
  solverConfig?: SolverConfig,
  startTime?: string,
};

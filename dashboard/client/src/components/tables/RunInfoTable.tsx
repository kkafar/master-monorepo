import "./css/Table.css";
import GenericTable from "./GenericTable";

export type RunInfoTableRowData = {
  expname: string;
  age_std: number;
  age_max: number;
  unique_sols: number;
  indiv_count_avg: number;
  indiv_count_std: number;
  co_inv_max: number;
  co_inv_min: number;
  fitness_best: number;
  total_time_avg: number;
  total_time_std: number;
};

const RunInfoTable = GenericTable<RunInfoTableRowData>;
export default RunInfoTable;

import "./css/Table.css";
import GenericTable from "./GenericTable";

export type ConvergenceInfoTableRowData = {
  expname: string;
  avg_cvg_iter: number;
  std_cvg_iter: number;
  median_cvg_iter: number;
  min_cvg_iter: number;
  max_cvg_iter: number;
  bks_hitratio: number;
  pre400_bks_hitratio: number;
};

const ConvergenceInfoTable = GenericTable<ConvergenceInfoTableRowData>;
export default ConvergenceInfoTable;

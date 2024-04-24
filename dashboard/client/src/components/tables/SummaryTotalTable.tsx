import GenericTable from "./GenericTable";

export type SummaryTotalTableRowData = {
  n_instances: number;
  bks_hit_total: number;
  avg_dev_to_bks: number;
};

export type SummaryTotalTableData = SummaryTotalTableRowData[];

const SummaryTotalTable = GenericTable<SummaryTotalTableRowData>;
export default SummaryTotalTable;

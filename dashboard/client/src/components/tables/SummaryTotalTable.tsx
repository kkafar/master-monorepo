
export type SummaryTotalTableRowData = {
  n_instances: number;
  bks_hit_total: number;
  avg_dev_to_bks: number;
};

export type SummaryTotalTableData = SummaryTotalTableRowData[];

type SummaryTotalTableProps = {
  data: SummaryTotalTableData;
};

type SummaryTotalTableRowProps = {
  data: SummaryTotalTableRowData;
};

export function SummaryTotalTableRow({ data }: SummaryTotalTableRowProps): React.JSX.Element {
  return (
    <tr>
      <td>{data.n_instances}</td>
      <td>{data.bks_hit_total}</td>
      <td>{data.avg_dev_to_bks}</td>
    </tr>
  );
}

export default function SummaryTotalTable({ data }: SummaryTotalTableProps): React.JSX.Element {
  return (
    <table>
      <thead>
        <tr>
          <th>n_instances</th>
          <th>bks_hit_total</th>
          <th>avg_dev_to_bks</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => <SummaryTotalTableRow key={i.toString()} data={row} />)}
      </tbody>
    </table>
  )
}


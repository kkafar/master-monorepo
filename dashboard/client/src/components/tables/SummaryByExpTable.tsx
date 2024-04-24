import "./css/Table.css"

export type SummaryByExpTableRowData = {
  expname: string;
  fitness_avg: number;
  fitness_best: number;
  bks: number;
  fitness_avg_to_bks_dev: number;
  diversity_avg: number;
  diversity_std: number;
  fitness_n_improv_avg: number;
  fitness_n_improv_std: number;
  bks_hitratio: number;
  itertime_avg: number;
  itertime_std: number;
};

export type SummaryByExpTableData = SummaryByExpTableRowData[];

export type SummaryByExpTableProps = {
  data: SummaryByExpTableData;
}

export type SummaryByExpTableRowProps = {
  data: SummaryByExpTableRowData;
}

export function SummaryByExpTableRow({ data }: SummaryByExpTableRowProps): React.JSX.Element {
  let rowClass = "";

  if (data.fitness_best === data.bks) {
    rowClass += " bold-row";
  }

  return (
    <tr className={rowClass}>
      <td>{data.expname}</td>
      <td>{data.fitness_avg}</td>
      <td>{data.fitness_best}</td>
      <td>{data.bks}</td>
      <td>{data.fitness_avg_to_bks_dev}</td>
      <td>{data.diversity_avg}</td>
      <td>{data.diversity_std}</td>
      <td>{data.fitness_n_improv_avg}</td>
      <td>{data.fitness_n_improv_std}</td>
      <td>{data.bks_hitratio}</td>
      <td>{data.itertime_avg}</td>
      <td>{data.itertime_std}</td>
    </tr>
  );
}

export default function SummaryByExpTable({ data }: SummaryByExpTableProps): React.JSX.Element {
  return (
    <table>
      <thead>
        <tr>
          <th>expname</th>
          <th>fitness_avg</th>
          <th>fitness_best</th>
          <th>bks</th>
          <th>fitness_avg_to_bks_dev</th>
          <th>diversity_avg</th>
          <th>diversity_std</th>
          <th>fitness_n_improv_avg</th>
          <th>fitness_n_improv_std</th>
          <th>bks_hitratio</th>
          <th>itertime_avg</th>
          <th>itertime_std</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => <SummaryByExpTableRow key={i.toString()} data={row} />)}
      </tbody>
    </table>
  );
}

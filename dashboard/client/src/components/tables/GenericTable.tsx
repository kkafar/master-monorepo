import "./css/Table.css";

export type RowRecord = Record<string, string | number>;

export interface RowProps<T extends RowRecord> {
  data: T;
};

export function GenericTableRow<RowDataT extends RowRecord>({ data }: RowProps<RowDataT>) {
  // type RowKeysT = keyof typeof data;
  // type RowValuesT = typeof data[RowKeysT];
  return (
    <tr>
      {Object.entries(data).map(([_key, value], i) => <td key={i.toString()}>{value}</td>)}
    </tr>
  );
}

export interface GenericTableProps<RowDataT extends RowRecord> {
  data: RowDataT[];
  RowComponent?: React.ComponentType<RowProps<RowDataT>>;
}

export default function GenericTable<RowDataT extends RowRecord>(props: GenericTableProps<RowDataT>) {
  const {
    data,
    RowComponent = GenericTableRow,
  } = props;

  return (
    <table>
      <thead>
        <tr>
          {data.length > 0 ? Object.entries(data[0]).map(([key, _value]) => <th>{key}</th>) : "No data"}
        </tr>
      </thead>
      <tbody>
        {data.map((row, i) => <RowComponent key={i.toString()} data={row} />)}
      </tbody>
    </table>
  );
}

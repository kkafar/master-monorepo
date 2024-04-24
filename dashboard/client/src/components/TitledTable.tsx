import React from "react";
import "./css/TitledTable.css";


export type TitledTableProps = {
  tableComponentFactory: () => React.ReactNode;
};

export default function TitledTable({ tableComponentFactory }: TitledTableProps): React.JSX.Element {
  return (
    <div className="margin-bottom">
      {tableComponentFactory()}
    </div>
  );
}

from typing import Any
from dataclasses import dataclass


@dataclass
class NodeMetadata:
    name: str


class ProcessingNode:
    def __init__(self, metadata: NodeMetadata):
        self.metadata: NodeMetadata = metadata

    def accept(self, data: Any) -> Any:
        raise NotImplementedError


class DataProcessingStrategy(ProcessingNode):
    def __init__(self, nodes: list[ProcessingNode] = [], metadata: NodeMetadata = NodeMetadata('unnamed')):
        super(ProcessingNode, self).__init__(metadata)
        self.nodes: list[ProcessingNode] = nodes

    def add_node(self, node: ProcessingNode) -> 'DataProcessingStrategy':
        self.nodes.append(node)
        return self

    def execute(self, data: Any) -> Any:
        raise NotImplementedError

    def accept(self, data: Any) -> Any:
        return self.execute(data)


class PipelineExecutor(DataProcessingStrategy):
    DEFAULT_META = NodeMetadata('PipelineExecutor')

    def __init__(self,
                 nodes: list[ProcessingNode] = [],
                 metadata: NodeMetadata = DEFAULT_META):
        super().__init__(nodes, metadata)

    def execute(self, data: Any) -> Any:
        last_result = data
        for node in self.nodes:
            last_result = node.accept(last_result)
        return last_result


class FanOutExecutor(DataProcessingStrategy):
    DEFAULT_META = NodeMetadata('FanOutExecutor')

    def __init__(self,
                 nodes: list[ProcessingNode] = [],
                 metadata: NodeMetadata = DEFAULT_META):
        super().__init__(nodes, metadata)

    def execute(self, data: Any) -> Any:
        for node in self.nodes:
            node.accept(data)


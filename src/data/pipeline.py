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
    def __init__(self, nodes: list[ProcessingNode] = []):
        super().__init__(nodes, NodeMetadata(name='PipelineExecutor'))

    def execute(self, data: Any) -> Any:
        last_result = data
        for node in self.nodes:
            last_result = node.accept(last_result)
        return last_result


class FanOutExecutor(DataProcessingStrategy):
    def __init__(self, nodes: list[ProcessingNode] = []):
        super().__init__(nodes, NodeMetadata(name='FanOutExecutor'))

    def execute(self, data: Any) -> Any:
        for node in self.nodes:
            node.accept(data)


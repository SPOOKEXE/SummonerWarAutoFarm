
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass
class Vector2:
	x : int = field(default=0)
	y : int = field(default=0)

	def __repr__(self) -> str:
		return f'Vector2({self.x}, {self.y})'

	def __str__(self) -> str:
		return f'Vector2({self.x}, {self.y})'

	def __hash__(self) -> str:
		return hash((self.x, self.y))

@dataclass
class Node:
	id : str
	root : bool = False
	depth : int = field(default=0)
	inputs : list[str] = field(default_factory=list)
	outputs : list[str] = field(default_factory=list)
	data : Any = field(default=None)

	def __repr__(self) -> str:
		return f'Node({self.id}, {self.depth}, {self.outputs})'

	def __str__(self) -> str:
		return f'Node({self.id}, {self.depth}, {self.outputs})'

	def __hash__(self) -> str:
		return hash((self.id, self.depth))

class NodeMap:
	nodes : list[Node] = field(default_factory=list)
	id_map : dict[str, Node] = field(default_factory=dict)
	edges_forward : dict[str, list[str]] = field(default_factory=dict)
	edges_reverse : dict[str, list[str]] = field(default_factory=dict)
	cache : dict[str, list[str]] = field(default_factory=dict)

	def __init__( self : NodeMap, nodes : list[Node] ) -> NodeMap:
		self.nodes = nodes
		self.rebuild()

	def __repr__(self) -> str:
		return f'NodeMap({self.edges_forward}, {self.edges_reverse})'

	def __str__(self) -> str:
		return f'NodeMap({self.edges_forward}, {self.edges_reverse})'

	def rebuild( self ) -> None:
		'''
		Rebuild the NodeMap:
		- clear old values (nodes, id_map, edges, cache).
		- setup 'id_map', 'edges' and 'depth' (individual nodes).
		- validate all node outputs exist and there is only one root.
		'''
		self.id_map = dict()
		self.edges_forward = dict()
		self.edges_reverse = dict()
		self.cache = dict()

		frontier : list[Node] = []
		searched : list[Node] = []
		hasRoot : bool = False

		for node in nodes:
			self.id_map[node.id] = node
			self.edges_forward[node.id] = node.outputs
			if node.root is True:
				frontier.append(node)
				if hasRoot is True:
					raise ValueError('You cannot have more than one root node.')
				hasRoot = True
		if hasRoot is False:
			raise ValueError('At least one Node must be a root point.')

		depth : int = 0
		while len(frontier) != 0:
			# take the temporary array out
			items : list[Node] = frontier.copy()
			frontier : list[Node] = []
			# iterate over each node
			for item in items:
				# set the item depth
				item.depth = depth
				for output_id in item.outputs:
					# check if the node exists
					output_node : Node | None = self.id_map.get(output_id)
					if output_node == None:
						raise ValueError(f'Node {item.id} has a non-existent output {output_id}')
					if not item.id in output_node.inputs:
						output_node.inputs.append(item.id)
					# skip already searched ones
					if not output_node in searched:
						searched.append(output_node)
						frontier.append(output_node)
			depth += 1

		for node in nodes:
			self.edges_reverse[node.id] = node.inputs

	def node_distance( self : NodeMap, node_a : Node, node_b : Node ) -> float | int:
		return abs(node_b.depth - node_a.depth)

	def get_cost( self : NodeMap, node_a : Node, node_b : Node, current : int | float, start : Node, goal : Node ) -> float | int:
		return current + self.node_distance(node_a, node_b) + self.node_distance(node_b, goal)

	def hash_path( self : NodeMap, start : Node, goal : Node ) -> str:
		return str(start.id) + '|' + str(goal.id)

	def pathfind( self : NodeMap, start_id : str, goal_id : str ) -> list[Node] | None:
		'''A* Pathfinding Implementation for directional graphs.'''
		start_node : Node = self.id_map[start_id]
		goal_node : Node = self.id_map[goal_id]

		# check for the cache
		pathkey : str = self.hash_path( start_node, goal_node )
		if self.cache.get(pathkey) != None:
			return self.cache[pathkey]

		# frontier search
		frontier : list[str] = [ start_id ]
		cameFrom : dict[str, str | bool] = { start_id : False }
		costTable : dict[str, int | float] = { start_id : 1 }
		active_id : str = None

		# algorithm
		steps = 0
		while len(frontier) > 0:
			steps += 1
			if goal_id in frontier:
				active_id : str = goal_id
				break
			active_id : str = frontier.pop(0)
			active_node : Node = self.id_map[active_id]
			items : list[str] = []
			items.extend( self.edges_forward[active_id] ) # forward traversing
			items.extend( self.edges_reverse[active_id] ) # backward traversing
			for point_id in items:
				point : Node = self.id_map[point_id]
				cost : int | float = self.get_cost( active_node, point, costTable.get(point_id) or 1, start_node, goal_node )
				if cameFrom.get(point_id) != None:
					if cost < costTable[point_id]:
						costTable[point_id] = cost
						cameFrom[point_id] = active_id
						frontier.insert(0, point_id)
				else:
					costTable[point_id] = cost
					cameFrom[point_id] = active_id
					frontier.append(point_id)
			# print( costTable )
			frontier.sort(key=lambda x: costTable[ x ], reverse=False)

		# check for path to goal
		if active_id is goal_id:
			resolvedPath = []
			while active_id and active_id != start_id:
				resolvedPath.append( self.id_map[active_id] )
				active_id : str = cameFrom[active_id]
			if self.cache is not None:
				self.cache[pathkey] = resolvedPath
			resolvedPath.reverse()
			return resolvedPath

		# no path to goal
		return None

if __name__ == '__main__':

	# create nodes
	# (0 -> 1 -> 3), (0 -> 2 -> 4 -> 5)
	nodes : list[Node] = [
		Node(id='0', root=True, outputs=['1', '2']),
		Node(id='1', outputs=['3']),
		Node(id='2', outputs=['4']),
		Node(id='3', outputs=[]),
		Node(id='4', outputs=['5']),
		Node(id='5', outputs=[]),
	]

	mapping = NodeMap(nodes=nodes)
	print(mapping)

	# forward traversing
	path : list[Node] | None = mapping.pathfind( '0', '5' )
	print([n.id for n in path])

	# backward traversing
	path : list[Node] | None = mapping.pathfind( '5', '0' )
	print([n.id for n in path])
